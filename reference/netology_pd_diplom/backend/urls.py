from django.urls import path
from django_rest_passwordreset.views import (
    reset_password_request_token,
    reset_password_confirm
)

from backend.views import (
    RegisterAccount, ConfirmAccount, LoginAccount, AccountDetails,
    CategoryView, ShopView, ProductInfoView, BasketView, OrderView,
    PartnerUpdate, PartnerState, PartnerOrders, PartnerExport,
    ContactView, ResultsView
)

app_name = 'backend'
urlpatterns = [
    # Partner endpoints
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('partner/state', PartnerState.as_view(), name='partner-state'),
    path('partner/orders', PartnerOrders.as_view(), name='partner-orders'),
    path('partner/export', PartnerExport.as_view(), name='partner-export'),

    # User endpoints
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path(
        'user/register/confirm',
        ConfirmAccount.as_view(),
        name='user-register-confirm'
    ),
    path('user/details', AccountDetails.as_view(), name='user-details'),
    path('user/contact', ContactView.as_view(), name='user-contact'),
    path('user/login', LoginAccount.as_view(), name='user-login'),
    path(
        'user/password_reset',
        reset_password_request_token,
        name='password-reset'
    ),
    path(
        'user/password_reset/confirm',
        reset_password_confirm,
        name='password-reset-confirm'
    ),

    # Catalog endpoints
    path('categories', CategoryView.as_view(), name='categories'),
    path('shops', ShopView.as_view(), name='shops'),
    path('products', ProductInfoView.as_view(), name='products'),

    # Order endpoints
    path('basket', BasketView.as_view(), name='basket'),
    path('order', OrderView.as_view(), name='order'),

    # Other endpoints
    path('results', ResultsView.as_view(), name='results'),
]
