from django.urls import path
from .views import sales_reports

urlpatterns = [
    path('/sales_reports', sales_reports, name='sales_reports'),
]