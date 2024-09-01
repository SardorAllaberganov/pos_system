from django.urls import path
from .views import all_categories

urlpatterns = [
    path("/all", all_categories, name="all_categories"),
]
