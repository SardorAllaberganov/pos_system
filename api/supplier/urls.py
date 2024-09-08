from django.urls import path
from .views import supplier_list, supplier_detail, create_supplier, update_supplier, delete_supplier

urlpatterns = [
    path('/all', supplier_list, name='suppliers_list'),
    path('/<int:supplier_id>', supplier_detail, name='supplier_detail'),
    path('/create', create_supplier, name='create_supplier'),
    path('/update/<int:supplier_id>', update_supplier, name='update_supplier'),
    path('/delete/<int:supplier_id>', delete_supplier, name='delete_supplier'),
]
