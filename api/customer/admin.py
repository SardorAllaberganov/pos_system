from django.contrib import admin
from .models import Customer

class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", 'name', 'email', "phone_number", "address", 'loyalty_points')
    search_fields = ("__all__",)
    readonly_fields = ["loyalty_points"]

admin.site.register(Customer, CustomerAdmin)
