from django.urls import path
from .views import all_customers

urlpatterns = [
    path('/all', all_customers, name='all_customers'),
]