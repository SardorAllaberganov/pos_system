from django.urls import path
from .views import all_categories, category_detail, create_category, update_category, delete_category, \
    all_subcategories, subcategory_detail, create_subcategory, update_subcategory, delete_subcategory

urlpatterns = [
    # category urls

    path("/all", all_categories, name="all_categories"),
    path("/<int:category_id>", category_detail, name="category_detail"),
    path("/create", create_category, name="create_category"),
    path("/update/<int:category_id>", update_category, name="update_category"),
    path("/delete/<int:category_id>", delete_category, name="delete_category"),

    # subcategory urls

    path("/subcategories", all_subcategories, name="all_subcategories"),
    path("/subcategories/<int:subcategory_id>", subcategory_detail, name="subcategory_detail"),
    path("/subcategories/create", create_subcategory, name="create_subcategory"),
    path("/subcategories/update/<int:subcategory_id>", update_subcategory, name="update_subcategory"),
    path("/subcategories/delete/<int:subcategory_id>", delete_subcategory, name="delete_subcategory"),
]
