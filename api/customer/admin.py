from django.contrib import admin
from .models import Customer


class CustomerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Customer._meta.get_fields()]
    search_fields = ("__all__",)
    readonly_fields = ["loyalty_points"]


admin.site.register(Customer, CustomerAdmin)
