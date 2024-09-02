from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.category.models import Category

from .serializers import CategorySerializer

@api_view(["GET"])
@permission_classes([AllowAny])
def all_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def category_detail(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    except Category.DoesNotExist:
        return Response({'message': "Category not found"}, status=404)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_category(request):
    if request.method == 'POST':
        user = request.user
        if user.role != 'Admin' and user.role != 'Manager':
            return Response({"error": "Permission denied. Only admins or managers can create a category."},
                            status=403)
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_category(request, category_id):
    if request.method == 'PUT':
        user = request.user
        if user.role != "Admin" and user.role != "Manager":
            return Response({"error": "Permission denied. Only admins or managers can update category."}, status=403)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'message': "Category not found"}, status=404)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
