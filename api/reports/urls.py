from django.urls import path
from .views import sales_reports, inventory_reports, customer_reports, employee_performance_reports

urlpatterns = [
    path('/sales_reports', sales_reports, name='sales_reports'),
    path('/inventory_reports', inventory_reports, name='inventory_reports'),
    path('/customer_reports', customer_reports, name='customer_reports'),
    path('/employees_reports', employee_performance_reports, name='employee_performance_report'),
]
