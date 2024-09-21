from django.urls import path
from .views import all_customers, customer_detail, create_customer, update_customer, delete_customer

urlpatterns = [
    path('/all', all_customers, name='all_customers'),
    path('/<int:customer_id>', customer_detail, name='customer_detail'),
    path('/create', create_customer, name='create_customer'),
    path('/update/<int:customer_id>', update_customer, name='update_customer'),
    path('/delete/<int:customer_id>', delete_customer, name='delete_customer'),
]
