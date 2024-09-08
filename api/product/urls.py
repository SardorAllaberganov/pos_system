from django.urls import path
from .views import all_products, product_detail

urlpatterns = [
    path('/all', all_products, name='all_products'),
    path('/<int:product_id>', product_detail, name='product_detail')
]
