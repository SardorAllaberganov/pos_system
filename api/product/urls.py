from django.urls import path
from .views import all_products

urlpatterns = [
    path('/all', all_products, name='all_products'),
]


