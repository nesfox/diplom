from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.validators import URLValidator
from rest_framework.generics import ListAPIView
from yaml import load as load_yaml
from yaml import Loader
from requests import get
from django.db.models import F, Sum

from backend.models import Shop, Order
from backend.serializers import (
    ShopSerializer,
    PartnerExportSerializer,
    OrderSerializer
)


class PartnerUpdate(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.type != 'shop':
            return Response(
                {'Status': False, 'Error': 'Только для магазинов'},
                status=403
            )

        url = request.data.get('url')
        if url:
            try:
                validate_url = URLValidator()
                validate_url(url)
                stream = get(url).content
                data = load_yaml(stream, Loader=Loader)

                # Обработка данных магазина
                return Response({'Status': True})
            except Exception as e:
                return Response(
                    {'Status': False, 'Errors': str(e)},
                    status=400
                )
        return Response(
            {
                'Status': False,
                'Errors': 'Не указаны все необходимые аргументы'
            },
            status=400
        )


class PartnerState(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.type != 'shop':
            return Response(
                {'Status': False, 'Error': 'Только для магазинов'},
                status=403
            )

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.type != 'shop':
            return Response(
                {'Status': False, 'Error': 'Только для магазинов'},
                status=403
            )

        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(
                    user_id=request.user.id).update(
                        state=str_to_bool(state)
                    )
                return Response({'Status': True})
            except ValueError as error:
                return Response({'Status': False, 'Errors': str(error)})

        return Response(
            {
                'Status': False,
                'Errors': 'Не указаны все необходимые аргументы'
            },
            status=400
        )


class PartnerOrders(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        if not (
            self.request.user.is_authenticated or
            self.request.user.type != 'shop'
        ):
            return Order.objects.none()
        return Order.objects.filter(
            ordered_items__product_info__shop__user_id=self.request.user.id
        ).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter'
        ).select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') *
                          F('ordered_items__product_info__price'))
        ).distinct()


class PartnerExport(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'},
                status=403
            )

        if request.user.type != 'shop':
            return Response(
                {'Status': False, 'Error': 'Только для магазинов'},
                status=403
            )

        shop = request.user.shop
        serializer = PartnerExportSerializer(shop)
        return Response(serializer.data)
