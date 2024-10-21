from django.urls import path
from .views import telegram_webhook, start_bot_view

urlpatterns = [
    path('webhook/', telegram_webhook, name='telegram_webhook'),
    path('start-bot/', start_bot_view, name='start_bot_view'),
]
