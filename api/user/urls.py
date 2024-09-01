from django.urls import path
from .views import (register_view, login_view, change_password, logout_view, change_user_details, change_user_role, )

urlpatterns = [
    path('/register', register_view, name='register'),
    path('/login', login_view, name='login'),
    path('/change_password', change_password, name='change_password'),
    path('/logout', logout_view, name='logout'),
    path('/change_user_details', change_user_details, name='change_user_details'),
    path('/change_user_role/<str:username>', change_user_role, name='change_user_role'),
]
