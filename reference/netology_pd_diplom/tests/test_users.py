import pytest
from django.urls import reverse
from rest_framework import status
from backend.models import User, ConfirmEmailToken, Contact


@pytest.mark.django_db
class TestUser:
    """Тесты для функционала пользователя"""

    def test_registration(self, client):
        """Тест регистрации пользователя"""
        url = reverse('backend:user-register')
        user_data = {
            'email': 'test@example.com',
            **NEW_USER_PROFILE_INFO
        }
        
        response = client.post(url, user_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'Status': True}
        
        user = User.objects.get(email=user_data['email'])
        for field, value in user_data.items():
            if field != 'password':
                assert getattr(user, field) == value

    def test_password_reset(self, client, user_buyer):
        """Тест сброса пароля"""
        response = client.post(
            reverse('backend:password-reset'),
            {'email': user_buyer.email}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'status': 'OK'}

    def test_user_details(self, client, token_buyer, user_buyer):
        """Тесты работы с профилем пользователя"""
        url = reverse('backend:user-details')
        client.credentials(HTTP_AUTHORIZATION=f'Token {token_buyer.key}')
        
        # Получение данных
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert set(response.json().keys()) >= {
            'id', 'first_name', 'last_name', 'email', 'company', 'position'
        }
        
        # Обновление данных
        update_data = {
            'first_name': 'Новое имя',
            'last_name': 'Новая фамилия',
            'email': user_buyer.email,
            'password': NEW_USER_PROFILE_INFO['password'],
            'company': 'Новая компания',
            'position': 'Новая должность'
        }
        response = client.post(url, update_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'Status': True}
        assert User.objects.get(id=user_buyer.id).first_name == 'Новое имя'

    def test_contact_operations(self, client, token_buyer, user_buyer):
        """Тесты работы с контактами пользователя"""
        url = reverse('backend:user-contact')
        client.credentials(HTTP_AUTHORIZATION=f'Token {token_buyer.key}')
        contact_data = {
            'city': 'Москва',
            'street': 'ул. Строителей',
            'house': '25',
            'structure': '1',
            'building': '1',
            'apartment': '13',
            'phone': '903-123-4567'
        }
        
        # Создание контакта
        response = client.post(url, contact_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'Status': True}
        assert Contact.objects.filter(user=user_buyer).count() == 1
        
        # Получение контактов
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        
        # Обновление контакта
        contact_id = response.json()[0]['id']
        response = client.put(url, {'id': contact_id, **contact_data})
        assert response.status_code == status.HTTP_200_OK
        
        # Удаление контакта
        response = client.delete(url, {'items': str(contact_id)})
        assert response.status_code == status.HTTP_200_OK
        assert Contact.objects.filter(user=user_buyer).count() == 0


@pytest.mark.django_db
class TestUserAuth:
    """Тесты авторизации и подтверждения email"""

    @pytest.mark.parametrize('valid_token', [True, False])
    def test_registration_confirm(self, client, valid_token):
        """Тест подтверждения email"""
        user = User.objects.create_user(
            email='test@example.com', 
            is_active=False, 
            **NEW_USER_PROFILE_INFO
        )
        
        token = ConfirmEmailToken.objects.get(user=user).key if valid_token else 'wrong'
        response = client.post(
            reverse('backend:user-register-confirm'),
            {'email': user.email, 'token': token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'Status': valid_token}
        assert User.objects.get(email=user.email).is_active == valid_token

    @pytest.mark.parametrize('valid_password', [True, False])
    def test_login(self, client, user_buyer, valid_password):
        """Тест авторизации"""
        password = NEW_USER_PROFILE_INFO['password'] if valid_password else 'wrong'
        response = client.post(
            reverse('backend:user-login'),
            {'email': user_buyer.email, 'password': password}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        if valid_password:
            assert data == {'Status': True, 'Token': data['Token']}
        else:
            assert data == {'Status': False, 'Errors': data['Errors']}