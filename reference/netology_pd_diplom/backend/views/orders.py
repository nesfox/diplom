from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F, Sum
from backend.models import Order
from backend.serializers import OrderSerializer


class BasketView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'},
                status=403
            )

        basket = Order.objects.filter(
            user_id=request.user.id, state='basket'
        ).prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter'
        ).annotate(
            total_sum=Sum(F('ordered_items__quantity') *
                          F('ordered_items__product_info__price'))
        ).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Реализация добавления в корзину
        pass


class OrderView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'},
                status=403
            )

        orders = Order.objects.filter(
            user_id=request.user.id
        ).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter'
        ).select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') *
                          F('ordered_items__product_info__price'))
        ).distinct()

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
