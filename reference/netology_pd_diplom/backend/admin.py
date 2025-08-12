from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import F, Sum
from backend.models import (
    User,
    Shop,
    Category,
    Product,
    ProductInfo,
    Parameter,
    ProductParameter,
    Order,
    OrderItem,
    Contact,
    ConfirmEmailToken
)


# ====================== USER ADMIN CONFIG ======================
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Расширенная админ-панель для управления пользователями"""
    model = User

    fieldsets = (
        # Основные данные
        (None, {
            'fields': ('email', 'password', 'type')
        }),

        # Персональная информация
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'company', 'position')
        }),

        # Права доступа
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
        }),

        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # Отображение в списке
    list_display = ('email', 'first_name', 'last_name', 'is_staff')


# ====================== BASIC MODEL ADMINS ======================
@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """Админка для магазинов"""
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий"""
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админка для продуктов"""
    pass


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    """Админка для информации о продуктах"""
    pass


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    """Админка для параметров"""
    pass


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    """Админка для параметров продуктов"""
    pass


# ====================== ORDER RELATED ADMINS ======================
class OrderItemsInline(admin.TabularInline):
    """Инлайн для отображения позиций заказа"""
    model = OrderItem
    list_display = (
        'product_info',
        'get_item_price',
        'quantity',
        'get_item_shop',
    )
    readonly_fields = list_display
    can_delete = False

    @admin.display(description='Цена')
    def get_item_price(self, obj):
        """Возвращает цену товара"""
        return obj.product_info.price

    @admin.display(description='Магазин')
    def get_item_shop(self, obj):
        """Возвращает магазин товара"""
        return obj.product_info.shop


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка для заказов с расчетом итоговой суммы"""
    inlines = [OrderItemsInline]
    list_display = ('user', 'dt', 'state', 'contact', 'order_sum')
    readonly_fields = ('user', 'dt', 'contact', 'order_sum')

    @admin.display(description='Сумма заказа (итого)')
    def order_sum(self, obj):
        """Рассчитывает общую сумму заказа"""
        total_sum = obj.ordered_items.aggregate(
            total_sum=Sum(F('quantity') * F('product_info__price'))
        )
        return total_sum.get('total_sum')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Админка для позиций заказа"""
    pass


# ====================== ADDITIONAL ADMINS ======================
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Админка для контактов"""
    pass


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    """Админка для токенов подтверждения email"""
    list_display = ('user', 'key', 'created_at')
