from django.contrib import admin
from .models import Account
from rest_framework.authtoken.models import Token


# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'email', 'phone_number', 'role', 'date_joined', 'last_login', 'token')

    @staticmethod
    def token(obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key
