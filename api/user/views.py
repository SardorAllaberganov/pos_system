from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegistrationSerializer, UpdateUserSerializer, UpdateUserRoleSerializer
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import AccessToken
from .models import Account

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
        else:
            data = serializer.errors
        return Response(data)

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    if request.method == "POST":
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            access = AccessToken.for_user(user)
            return Response({
                "token": str(access),
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
        return Response({"success": "Password updated successfully"}, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
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
def change_user_role(request, username):
    if request.method == "PUT":
        user = request.user

        if user.role != 'Admin' and user.role != 'Manager':
            return Response({"error": "Permission denied. Only admins or managers can update user roles."},
                            status=403)
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        serializer = UpdateUserRoleSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': "User role updated successfully"}, status=200)
        return Response(serializer.errors, status=400)


