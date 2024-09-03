from django.urls import path
from .views import all_categories, category_detail, create_category, update_category, delete_category

urlpatterns = [
    path("/all", all_categories, name="all_categories"),
    path("/<int:category_id>", category_detail, name="category_detail"),
    path("/create", create_category, name="create_category"),
    path("/update/<int:category_id>", update_category, name="update_category"),
    path("/delete/<int:category_id>", delete_category, name="delete_category"),
]
