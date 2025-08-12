from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django_rest_passwordreset.tokens import get_token_generator


STATE_CHOICES = (
    ('basket', 'Корзина'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
)


class UserManager(BaseUserManager):
    """Менеджер для работы с пользователями"""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Создание и сохранение пользователя с email и паролем"""
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Создание обычного пользователя"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Создание суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Суперпользователь должен иметь is_superuser=True'
            )

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Модель пользователя"""
    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = 'email'

    email = models.EmailField('Email', unique=True)
    company = models.CharField('Компания', max_length=40, blank=True)
    position = models.CharField('Должность', max_length=40, blank=True)
    username = models.CharField(
        'Логин',
        max_length=150,
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': "Пользователь с таким логином уже существует"
        },
    )
    is_active = models.BooleanField('Активен', default=False)
    type = models.CharField(
        'Тип пользователя',
        choices=USER_TYPE_CHOICES,
        max_length=5,
        default='buyer'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Shop(models.Model):
    """Модель магазина"""
    name = models.CharField('Название', max_length=50)
    url = models.URLField('Ссылка', null=True, blank=True)
    user = models.OneToOneField(
        User,
        verbose_name='Пользователь',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    state = models.BooleanField('Статус получения заказов', default=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель категории"""
    name = models.CharField('Название', max_length=40)
    shops = models.ManyToManyField(
        Shop,
        verbose_name='Магазины',
        related_name='categories',
        blank=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель продукта"""
    name = models.CharField('Название', max_length=80)
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='products',
        blank=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    """Модель информации о продукте"""
    model = models.CharField('Модель', max_length=80, blank=True)
    external_id = models.PositiveIntegerField('Внешний ID')
    product = models.ForeignKey(
        Product,
        verbose_name='Продукт',
        related_name='product_infos',
        blank=True,
        on_delete=models.CASCADE
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name='Магазин',
        related_name='product_infos',
        blank=True,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField('Количество')
    price = models.PositiveIntegerField('Цена')
    price_rrc = models.PositiveIntegerField('Рекомендуемая цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информация о продуктах'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'shop', 'external_id'],
                name='unique_product_info'
            ),
        ]

    def __str__(self):
        return self.product.name


class Parameter(models.Model):
    """Модель параметра"""
    name = models.CharField('Название', max_length=40)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """Модель параметра продукта"""
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name='Информация о продукте',
        related_name='product_parameters',
        blank=True,
        on_delete=models.CASCADE
    )
    parameter = models.ForeignKey(
        Parameter,
        verbose_name='Параметр',
        related_name='product_parameters',
        blank=True,
        on_delete=models.CASCADE
    )
    value = models.CharField('Значение', max_length=100)

    class Meta:
        verbose_name = 'Параметр продукта'
        verbose_name_plural = 'Параметры продуктов'
        constraints = [
            models.UniqueConstraint(
                fields=['product_info', 'parameter'],
                name='unique_product_parameter'
            ),
        ]


class Contact(models.Model):
    """Модель контактов пользователя"""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='contacts',
        blank=True,
        on_delete=models.CASCADE
    )
    city = models.CharField('Город', max_length=50)
    street = models.CharField('Улица', max_length=100)
    house = models.CharField('Дом', max_length=15, blank=True)
    structure = models.CharField('Корпус', max_length=15, blank=True)
    building = models.CharField('Строение', max_length=15, blank=True)
    apartment = models.CharField('Квартира', max_length=15, blank=True)
    phone = models.CharField('Телефон', max_length=20)

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'


class Order(models.Model):
    """Модель заказа"""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='orders',
        blank=True,
        on_delete=models.CASCADE
    )
    dt = models.DateTimeField(auto_now_add=True)
    state = models.CharField('Статус', choices=STATE_CHOICES, max_length=15)
    contact = models.ForeignKey(
        Contact,
        verbose_name='Контакт',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-dt',)

    def __str__(self):
        return str(self.dt)


class OrderItem(models.Model):
    """Модель позиции заказа"""
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        related_name='ordered_items',
        blank=True,
        on_delete=models.CASCADE
    )
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name='Информация о продукте',
        related_name='ordered_items',
        blank=True,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField('Количество')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'
        constraints = [
            models.UniqueConstraint(
                fields=['order_id', 'product_info'],
                name='unique_order_item'
            ),
        ]


class ConfirmEmailToken(models.Model):
    """Модель токена подтверждения email"""
    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    key = models.CharField('Ключ', max_length=64, db_index=True, unique=True)

    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """Генерация ключа подтверждения"""
        return get_token_generator().generate_token()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Токен подтверждения для {self.user}'
