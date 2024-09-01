from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users', include('api.user.urls')),
    path('api/categories', include('api.category.urls')),
]
