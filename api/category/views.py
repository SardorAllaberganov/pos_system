from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.category.models import Category, SubCategory
from .serializers import CategorySerializer, SubcategorySerializer
from api.core.decorators import check_role

##########################################
# Category views
##########################################
@api_view(["GET"])
@permission_classes([AllowAny])
def all_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response({"message": "Fetched all categories", "data": serializer.data}, status=200)

@api_view(["GET"])
@permission_classes([AllowAny])
def category_detail(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        serializer = CategorySerializer(category)
        return Response({"message": "Category fetched successfully", "data": serializer.data}, status=200)
    except Category.DoesNotExist:
        return Response({'message': "Category not found"}, status=404)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@check_role(["Admin", "Manager"])
def create_category(request):
    if request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category created successfully", "data": serializer.data}, status=201)
        return Response({"message": serializer.errors}, status=400)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_category(request, category_id):
    if request.method == 'PUT':
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'message': "Category not found"}, status=404)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category updated successfully", "data": serializer.data}, status=200)
        return Response({"message": serializer.errors}, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@check_role(["Admin", "Manager"])
def delete_category(request, category_id):
    if request.method == 'DELETE':
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return Response({'message': "Category successfully deleted"}, status=204)
        except Category.DoesNotExist:
            return Response({'message': "Category not found"}, status=404)

##########################################
# SubCategory views
##########################################

@api_view(['GET'])
@permission_classes([AllowAny])
def all_subcategories(request):
    subcategories = SubCategory.objects.all()
    serializer = SubcategorySerializer(subcategories, many=True)
    return Response(serializer.data)
