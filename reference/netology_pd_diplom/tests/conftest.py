import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from model_bakery import baker
from rest_framework.authtoken.models import Token
from backend.models import User, Shop, OrderItem, ProductInfo, Order, Product, Parameter, ProductParameter, Contact


NEW_USER = {
    'first_name': 'Иван',
    'last_name': 'Иванов',
    'password': 'очень_сложный_пароль_12345',
    'company': 'Компания Иванова Ивана',
    'position': 'Должность Иванова Ивана',
}


# Фикстуры клиента и фабрик
@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_buyer():
    user = User.objects.create_user(email='buyer@example.com', is_active=True, **NEW_USER)
    user.type = 'buyer'
    user.save()
    return user


@pytest.fixture
def user_shop():
    user = User.objects.create_user(email='shop@example.com', is_active=True, **NEW_USER)
    user.type = 'shop'
    user.save()
    return user


@pytest.fixture
def token_buyer(user_buyer):
    token, _ = Token.objects.get_or_create(user=user_buyer)
    return token


@pytest.fixture
def token_shop(user_shop):
    token, _ = Token.objects.get_or_create(user=user_shop)
    return token


@pytest.fixture
def active_shop(user_shop):
    shop = baker.make('backend.Shop', user=user_shop, state=True)
    return shop


# Фабрики моделей
model_factories = {
    'category': 'backend.Category',
    'shop': 'backend.Shop',
    'product': 'backend.Product',
    'product_info': 'backend.ProductInfo',
    'order': 'backend.Order',
    'order_item': 'backend.OrderItem',
    'parameter': 'backend.Parameter',
    'product_parameter': 'backend.ProductParameter',
    'contact': 'backend.Contact',
}

for name, model in model_factories.items():
    @pytest.fixture
    def factory(request, model=model):
        def maker(**kwargs):
            return baker.make(model, **kwargs)
        return maker
    globals()[f'{name}_factory'] = factory


# Комплексные фикстуры данных
@pytest.fixture
def shop_products(active_shop, product_factory, category_factory, product_info_factory, product_parameter_factory, parameter_factory):
    category = category_factory()
    parameters = parameter_factory(_quantity=3)
    products = product_factory(category=category, _quantity=3)
    
    for product in products:
        product_info = product_info_factory(product=product, shop=active_shop)
        for param in parameters:
            product_parameter_factory(product_info=product_info, parameter=param)
    
    return products


@pytest.fixture
def shop_orders(user_buyer, shop_products, order_factory, order_item_factory):
    orders = order_factory(user=user_buyer, state='new', _quantity=3)
    basket = order_factory(user=user_buyer, state='basket', _quantity=2)
    
    for order in orders + basket:
        for product in shop_products:
            order_item_factory(order=order, product_info=product.product_infos.first(), quantity=1)
    
    return orders + basket


@pytest.fixture
def basket(user_buyer, shop_products, order_factory, order_item_factory, contact_factory):
    contact = contact_factory(user=user_buyer)
    basket = order_factory(user=user_buyer, contact=contact, state='basket')
    
    for product in shop_products:
        order_item_factory(order=basket, product_info=product.product_infos.first(), quantity=1)
    
    return basket
