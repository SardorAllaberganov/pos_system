from django.urls import path
from .views import supplier_list, supplier_detail, create_supplier, update_supplier, delete_supplier, \
    supplier_order_total, supplier_orders, supplier_order_items, supplier_products

urlpatterns = [
    path('/all', supplier_list, name='suppliers_list'),
    path('/<int:supplier_id>', supplier_detail, name='supplier_detail'),
    path('/create', create_supplier, name='create_supplier'),
    path('/update/<int:supplier_id>', update_supplier, name='update_supplier'),
    path('/delete/<int:supplier_id>', delete_supplier, name='delete_supplier'),
    path('/total_order_amount/<int:supplier_id>', supplier_order_total, name='supplier_order_total'),
    path('/orders_list/<int:supplier_id>', supplier_orders, name='supplier_orders_list'),
    path('/<int:supplier_id>/order_items', supplier_order_items, name='supplier_order_items'),
    path('/products_list/<int:supplier_id>/', supplier_products, name='supplier_products'),
]
