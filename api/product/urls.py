from django.urls import path
from .views import all_products, product_detail, delete_product

urlpatterns = [
    path('/all', all_products, name='all_products'),
    path('/<int:product_id>', product_detail, name='product_detail'),
    path('/delete/<int:product_id>', delete_product, name='delete_product')
]
