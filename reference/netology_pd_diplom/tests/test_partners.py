import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import Shop, Order


@pytest.mark.django_db
class TestPartner:
    """Тесты для функционала партнера (магазина)"""
    
    def test_partner_update(self, client, token_shop):
        """Тест обновления прайса партнера"""
        url = reverse('backend:partner-update')
        client.credentials(HTTP_AUTHORIZATION=f'Token {token_shop.key}')
        data = {'url': 'https://raw.githubusercontent.com/bku4erov/py-diplom/master/data/shop1.yaml'}
        response = client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'Status': True,
            'Task_id': response.json().get('Task_id')
        }

    def test_partner_state_get(self, client, token_shop, active_shop):
        """Тест получения статуса партнера"""
        url = reverse('backend:partner-state')
        client.credentials(HTTP_AUTHORIZATION=f'Token {token_shop.key}')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'name': active_shop.name,
            'state': active_shop.state
        }

    def test_partner_state_post(self, client, token_shop, active_shop):
        """Тест обновления статуса партнера"""
        url = reverse('backend:partner-state')
        client.credentials(HTTP_AUTHORIZATION=f'Token {token_shop.key}')
        response = client.post(url, {'state': 'false'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'Status': True}
        assert Shop.objects.get(id=active_shop.id).state is False

    def test_partner_orders_get(self, client, token_shop, shop_orders):
        """Тест получения заказов партнера"""
        url = reverse('backend:partner-orders')
        client.credentials(HTTP_AUTHORIZATION=f'Token {token_shop.key}')
        response = client.get(url)
        data = response.json()
        
        assert response.status_code == status.HTTP_200_OK
        assert len(data) == len(shop_orders) - 2  # минус корзины
        assert all({'id', 'ordered_items'} <= set(order.keys()) for order in data)

    def test_partner_orders_put(self, client, token_shop, shop_orders):
        """Тест обновления статуса заказа"""
        url = reverse('backend:partner-orders')
        client.credentials(HTTP_AUTHORIZATION=f'Token {token_shop.key}')
        order_id = shop_orders[0].id
        response = client.put(url, {'id': order_id, 'state': 'sent'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'Status': True}
        assert Order.objects.get(id=order_id).state == 'sent'