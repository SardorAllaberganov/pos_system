from .models import Account
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = Account
        fields = ("email", "username", "password", "password2", 'name', 'phone_number', 'role')
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def save(self):
        account = Account(
            email=self.validated_data["email"],
            username=self.validated_data["username"],
            name=self.validated_data["name"],
            phone_number=self.validated_data["phone_number"],
            role=self.validated_data["role"],
        )
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise serializers.ValidationError({"password": "Passwords must match."})
        account.set_password(password)
        account.save()
        return account
