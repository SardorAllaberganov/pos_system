from django.urls import path
from .views import (register_view, login_view, change_password)

urlpatterns = [
    path('/register', register_view, name='register'),
    path('/login', login_view, name='login'),
    path('/change_password', change_password, name='change_password'),
]
