import os
from celery import Celery
from celery.result import AsyncResult


# Инициализация Celery приложения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netology_pd_diplom.settings')

celery_app = Celery('netology_diplom_backend')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()


def get_task(task_id: str) -> AsyncResult:
    """Возвращает результат асинхронной задачи Celery по её идентификатору.
    
    Args:
        task_id: Уникальный идентификатор задачи Celery
        
    Returns:
        Объект AsyncResult с состоянием и результатом выполнения задачи
    """
    return AsyncResult(task_id, app=celery_app)