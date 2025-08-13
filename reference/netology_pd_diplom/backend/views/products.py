from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.db.models import Q
from backend.models import Category, ProductInfo, Shop
from backend.serializers import (
    CategorySerializer,
    ProductInfoSerializer,
    ShopSerializer
)


class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer

    @method_decorator(cache_page(60*60*2))  # Кешируем на 2 часа
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @method_decorator(cache_page(60*60*2))  # Кешируем на 2 часа
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductInfoView(APIView):
    @method_decorator(cache_page(60*60))  # Кешируем на 1 час
    def get(self, request, *args, **kwargs):
        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query &= Q(shop_id=shop_id)
        if category_id:
            query &= Q(product__category_id=category_id)

        queryset = ProductInfo.objects.filter(
            query
        ).select_related(
            'shop', 'product__category'
        ).prefetch_related(
            'product_parameters__parameter'
        ).distinct()

        serializer = ProductInfoSerializer(queryset, many=True)
        return Response(serializer.data)
