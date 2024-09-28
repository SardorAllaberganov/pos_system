from django.urls import path
from .views import checkout_cart, get_receipt, get_receipt_pdf, get_all_sales

urlpatterns = [
    path('/checkout', checkout_cart, name='checkout'),
    path('/receipt/<int:sale_id>', get_receipt, name='receipt'),
    path('/receipt/pdf/<str:receipt_number>', get_receipt_pdf, name='get_receipt_pdf'),
    path('/all_sales', get_all_sales, name='all_sales'),
]
