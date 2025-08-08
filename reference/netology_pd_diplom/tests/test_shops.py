import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import Shop, Product, Order, OrderItem
from backend.serializers import ProductInfoSerializer


@pytest.mark.django_db
class TestShop:
    """Тесты для функционала магазина и покупателя"""

    def test_categories_get(self, client, category_factory):
        """Тест получения списка категорий"""
        categories = category_factory(_quantity=3)
        response = client.get(reverse('backend:categories'))
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert {'count', 'results'} <= set(data.keys())
        assert data['count'] == 3
        assert {c.name for c in categories} >= {item['name'] for item in data['results']}

    def test_shops_get(self, client, active_shop):
        """Тест получения списка магазинов"""
        response = client.get(reverse('backend:shops'))
        
        assert response.status_code == status.HTTP_200_OK
        assert active_shop.name == response.json()['results'][0]['name']

    def test_products_get(self, client, shop_products):
        """Тест получения списка продуктов"""
        response = client.get(reverse('backend:products'))
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(shop_products)
        assert set(ProductInfoSerializer.Meta.fields) <= set(response.json()[0].keys())

    def test_products_search(self, client, shop_products):
        """Тест фильтрации продуктов"""
        response = client.get(f"{reverse('backend:products')}?shop_id=0&category_id=0")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

    def test_basket_operations(self, client, token_buyer, shop_products):
        """Тесты работы с корзиной"""
        # Добавление товаров
        url = reverse('backend:basket')
        client.credentials(HTTP_AUTHORIZATION=f'Token {token_buyer.key}')
        
        items = [{"product_info": p.product_infos.first().id, "quantity": 3} 
                for p in shop_products[:2]]
        response = client.post(url, {'items': items})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'Status': True}
        order = Order.objects.filter(state='basket').first()
        assert order.ordered_items.count() == 2

        # Изменение количества
        item = order.ordered_items.first()
        response = client.put(url, {'items': [{"id": item.id, "quantity": 8}]})
        
        assert response.status_code == status.HTTP_200_OK
        assert OrderItem.objects.get(id=item.id).quantity == 8

        # Получение корзины
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()[0]['id'] == order.id
        assert len(response.json()[0]['ordered_items']) == 2

        # Удаление товаров
        to_delete = [item.id for item in order.ordered_items.all()[:1]]
        response = client.delete(url, {'items': to_delete})
        
        assert response.status_code == status.HTTP_200_OK
        assert order.ordered_items.count() == 1

    def test_orders(self, client, token_buyer, shop_orders, basket):
        """Тесты работы с заказами"""
        url = reverse('backend:order')
        client.credentials(HTTP_AUTHORIZATION=f'Token {token_buyer.key}')
        
        # Получение заказов
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len([o for o in shop_orders if o.state != 'basket'])

        # Создание заказа
        response = client.post(url, {'id': basket.id, 'contact': basket.contact.pk})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'Status': True}
        assert Order.objects.get(id=basket.id).state == 'new'