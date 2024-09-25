from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegistrationSerializer, UpdateUserSerializer, UpdateUserRoleSerializer
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from .models import Account
from api.core.decorators import check_role

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.views.decorators.cache import cache_page

from silk.profiling.profiler import silk_profile


@api_view(["POST"])
def register_view(request):
    if request.method == "POST":
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data["response"] = "successfully registered new user."
            data["email"] = account.email
            data["username"] = account.username
            data['phone_number'] = account.phone_number
            data['role'] = account.role
            token = Token.objects.get(user=account).key
            data["token"] = token
            return Response({"message": "User created successfully", "data": data})
        else:
            return Response({"message": serializer.errors})


@api_view(["POST"])
@permission_classes([AllowAny])
@cache_page(60*5)
@silk_profile(name='Login view')
def login_view(request):
    if request.method == "POST":
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            Token.objects.filter(user=user).delete()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,
            })
        else:
            # Return an error response if authentication fails
            return Response({"error": "Invalid credentials"}, status=400)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    if request.method == "PUT":
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_new_password = request.data.get("confirm_new_password")

        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect"}, status=400)

        if new_password != confirm_new_password:
            return Response({"error": "New password and confirm new password are incorrect"}, status=400)

        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

        user.set_password(new_password)
        user.save()

        # Update the session to prevent logging the user out after changing the password
        update_session_auth_hash(request, user)
        return Response({"message": "Password updated successfully"}, status=200)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except (AttributeError, Token.DoesNotExist):
        return Response({"error": "Token not found or already deleted"}, status=400)
    return Response({"message": "Logged out successfully"}, status=205)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def change_user_details(request):
    if request.method == "PUT":
        user = request.user
        serializer = UpdateUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
                "data": serializer.data
            }, status=200)
        return Response(serializer.errors, status=400)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@check_role(["admin", "manager"])
def change_user_role(request, username):
    if request.method == "PUT":
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        serializer = UpdateUserRoleSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': "User role updated successfully"}, status=200)
        return Response(serializer.errors, status=400)


@api_view(["delete"])
@permission_classes([IsAuthenticated])
@check_role(["admin", "manager"])
def delete_user(request, username):
    if request.method == "DELETE":
        try:
            account = Account.objects.get(username=username)
            account.delete()
            return Response({"message": "User deleted successfully"}, status=200)
        except Account.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    if request.method == "POST":
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        uid = urlsafe_base64_encode(force_bytes(account.id))
        token = default_token_generator.make_token(account)
        reset_link = f"http://127.0.0.1:8000/reset-password/{uid}/{token}"

        send_mail(
            subject="Password reset request",
            message=f"Please click the link to reset your password: {reset_link}",
            from_email="info@pos.com",
            recipient_list=[email],
        )
        return Response({"message": "Password reset link sent to your email", 'link': reset_link}, status=200)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_confirm(request, uidb64, token):
    if request.method == "POST":
        if not request.data.get("new_password"):
            return Response({"error": "New password is required"}, status=400)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            account = Account.objects.get(pk=uid)
        except (TypeError, ValueError, Account.DoesNotExist):
            return Response({"error": "Invalid token"}, status=400)

        account.set_password(request.data.get("new_password"))
        account.save()

        return Response({"message": "Password updated successfully"}, status=200)
