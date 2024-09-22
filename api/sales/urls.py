from django.urls import path
from .views import checkout_cart

urlpatterns = [
    path('/checkout', checkout_cart, name='checkout'),
]
