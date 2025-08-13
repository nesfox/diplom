from rest_framework.response import Response
from rest_framework.views import APIView
from netology_pd_diplom.celery_app import get_task


class ResultsView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Требуется авторизация'},
                status=403
            )

        task_id = request.data.get('task_id')
        if not task_id:
            return Response(
                {'Status': False, 'Errors': 'Не указан ID задачи'},
                status=400
            )

        try:
            task = get_task(task_id)
            return Response({
                'Status': True,
                'Task_id': task_id,
                'State': task.state,
                'Results': task.result if task.state == 'SUCCESS'
                else str(task.result)
            })
        except Exception:
            return Response(
                {'Status': False, 'Errors': f'Задача {task_id} не найдена'},
                status=404
            )
