from django.urls import path
from .views import get_cart, add_to_cart, update_cart, remove_cart_item, clear_cart

urlpatterns = [
    path('/get', get_cart, name='get_cart'),
    path('/add_to_cart', add_to_cart, name='add_to_cart'),
    path('/update_cart/<int:cart_item_id>', update_cart, name='update_cart'),
    path('/remove/<int:cart_item_id>', remove_cart_item, name='remove_cart_item'),
    path('/clear_cart/<int:cart_id>', clear_cart, name='clear_cart'),
]
