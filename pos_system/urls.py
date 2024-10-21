from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="POS System API",
        default_version='v1',
        description="API documentation for your project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="your_email@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),

)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users', include('api.user.urls')),
    path('api/categories', include('api.category.urls')),
    path('api/suppliers', include('api.supplier.urls')),
    path('api/products', include('api.product.urls')),
    path('api/customers', include('api.customer.urls')),
    path('api/cart', include('api.cart.urls')),
    path('api/sales', include('api.sales.urls')),
    path('api/reports', include('api.reports.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('bot/', include('api.telegrambot.urls'))

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

import requests


WEBHOOK_URL = 'https://localhost:8000/api/webhook/'

# Set the webhook
requests.post(f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook', data={'url': WEBHOOK_URL})
