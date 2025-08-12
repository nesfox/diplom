from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from yaml import load as load_yaml, Loader
from backend.models import (
    Shop,
    Category,
    Product,
    ProductInfo,
    Parameter,
    ProductParameter
)
from backend.serializers import PartnerExportSerializer


@shared_task
def send_email(title, message, sender, recipients):
    """Асинхронная отправка email через Celery."""
    email = EmailMultiAlternatives(
        subject=title,
        body=message,
        from_email=sender,
        to=recipients
    )
    email.send()


@shared_task
def partner_export(user_id):
    """Экспорт данных партнера в фоновом режиме."""
    shop = Shop.objects.filter(user_id=user_id).first()
    return PartnerExportSerializer(shop).data


@shared_task
def partner_update(stream, user_id):
    """Фоновое обновление прайс-листа партнера."""
    data = load_yaml(stream, Loader=Loader)

    # Обновление магазина и категорий
    shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=user_id)

    for category in data['categories']:
        category_obj, _ = Category.objects.get_or_create(
            id=category['id'],
            name=category['name']
        )
        category_obj.shops.add(shop.id)
        category_obj.save()

    # Очистка старых товаров
    ProductInfo.objects.filter(shop_id=shop.id).delete()

    # Импорт новых товаров
    for item in data['goods']:
        product, _ = Product.objects.get_or_create(
            name=item['name'],
            category_id=item['category']
        )

        product_info = ProductInfo.objects.create(
            product_id=product.id,
            external_id=item['id'],
            model=item['model'],
            price=item['price'],
            price_rrc=item['price_rrc'],
            quantity=item['quantity'],
            shop_id=shop.id
        )

        # Обработка параметров товара
        for name, value in item['parameters'].items():
            param, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.create(
                product_info_id=product_info.id,
                parameter_id=param.id,
                value=value
            )
