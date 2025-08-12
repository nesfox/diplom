from typing import Type

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from backend.models import ConfirmEmailToken, User
from backend.celery_tasks import send_email

new_user_registered = Signal()

new_order = Signal()


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender,
    instance,
    reset_password_token,
    **kwargs
):
    """Отправка письма с токеном сброса пароля"""
    send_email.delay_on_commit(
        title=f"Сброс пароля для {reset_password_token.user}",
        message=reset_password_token.key,
        sender=settings.EMAIL_HOST_USER,
        recipients=[reset_password_token.user.email],
    )


@receiver(post_save, sender=User)
def new_user_registered_signal(
    sender: Type[User],
    instance: User,
    created: bool,
    **kwargs
):
    """Отправка письма с подтверждением email при регистрации"""
    if created and not instance.is_active:
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk)
        send_email.delay_on_commit(
            title=f"Подтверждение email для {instance.email}",
            message=token.key,
            sender=settings.EMAIL_HOST_USER,
            recipients=[instance.email],
        )


@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """Отправка уведомления о новом заказе"""
    user = User.objects.get(id=user_id)
    send_email.delay_on_commit(
        title="Обновление статуса заказа",
        message="Ваш заказ успешно сформирован",
        sender=settings.EMAIL_HOST_USER,
        recipients=[user.email],
    )
