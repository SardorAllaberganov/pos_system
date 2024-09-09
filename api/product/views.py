from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.product.models import Product
from .serializers import ProductSerializer
from api.core.paginator import CustomPagination
from api.core.decorators import check_role


@api_view(['GET'])
@permission_classes([AllowAny])
def all_products(request):
    products = Product.objects.all()
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
@check_role(["Admin", "Manager"])
def delete_product(request, product_id):
    if request.method == "DELETE":
        try:
            product = Product.objects.get(pk=product_id)
            product.delete()
            return Response({"message": "Product deleted successfully"}, status=200)
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=404)
