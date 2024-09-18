from django.urls import path
from .views import all_products, product_detail, delete_product, update_product, create_product, product_export_csv

urlpatterns = [
    path('/all', all_products, name='all_products'),
    path('/<int:product_id>', product_detail, name='product_detail'),
    path('/delete/<int:product_id>', delete_product, name='delete_product'),
    path('/update/<int:product_id>', update_product, name='update_product'),
    path('/create', create_product, name='create_product'),
    path('/export_csv', product_export_csv, name='product_export_csv'),
]
