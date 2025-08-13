"""netology_pd_diplom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
import time


def trigger_error(request):
    """Тестовая view для проверки интеграции Sentry.

    Намеренно вызывает ошибку деления на ноль для тестирования Sentry.
    В production должен быть заменен на корректную обработку ошибок.
    """
    division_by_zero = 1 / 0  # Намеренная ошибка для Sentry
    return HttpResponse(division_by_zero)


def simulate_long_request(request):
    """Тестовая view для проверки мониторинга производительности.

    Имитирует долгий запрос (4 секунды) для тестирования
    производительности в Sentry.
    """
    time.sleep(4)
    return HttpResponse("Long request completed")


urlpatterns = [
    # Админка и Jet
    path('jet/', include('jet.urls', 'jet')),
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/v1/', include('backend.urls', namespace='backend')),

    # Документация API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    path(
        'api/schema/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),

    # Профилирование
    path('silk/', include('silk.urls', namespace='silk')),

    # Тестовые endpoints для мониторинга
    path('sentry-debug/', trigger_error),
    path('performance-test/', simulate_long_request),
]
