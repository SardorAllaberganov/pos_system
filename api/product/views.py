from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
import pandas as pd
import csv
from api.product.models import Product
from .serializers import ProductSerializer
from api.core.paginator import CustomPagination
from api.core.decorators import check_role
from django.db.models import Q
from django.views.decorators.cache import cache_page


@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60*15)
def all_products(request):
    search = request.GET.get('search', None)
    category = request.GET.get('category', None)
    subcategory = request.GET.get('subcategory', None)

    products = Product.objects.all()

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(barcode__icontains=search)
        )

    if category:
        products = products.filter(
            Q(subcategory__category__name__icontains=category)
        )

    if subcategory:
        products = products.filter(
            Q(subcategory__name__icontains=subcategory)
        )

    paginator = CustomPagination()
    paginated_products = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(paginated_products, many=True)
    return Response({"message": "All products fetched successfully", "data": serializer.data}, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def product_detail(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({"message": "Product not found"}, status=404)

    serializer = ProductSerializer(product)
    return Response({"message": "Product fetched successfully", "data": serializer.data}, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@check_role(['admin', 'manager'])
def delete_product(request, product_id):
    if request.method == "DELETE":
        try:
            product = Product.objects.get(pk=product_id)
            product.delete()
            return Response({"message": "Product deleted successfully"}, status=200)
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=404)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@check_role(['admin', 'manager'])
def update_product(request, product_id):
    if request.method == "PUT":
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=404)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product updated successfully", "data": serializer.data}, status=200)
        else:
            return Response({"error": serializer.errors}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@check_role(["admin", 'manager'])
def create_product(request):
    if request.method == "POST":
        data = request.data.copy()
        data['creator'] = request.user.id
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product created successfully", "data": serializer.data}, status=200)
        return Response({"error": serializer.errors}, status=400)


@api_view(["GET"])
@permission_classes([AllowAny])
def product_export_csv(request):
    if request.method == "GET":
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        writer = csv.writer(response)
        df = pd.json_normalize(serializer.data)
        field_names = list(df.columns)
        writer.writerow(field_names)
        for index, row in df.iterrows():
            writer.writerow(row)

        return response
