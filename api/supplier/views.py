from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from api.product.models import Product
from api.product.serializers import ProductSerializer
from api.supplier.models import Supplier, PurchaseOrder, PurchaseOrderItem
from api.supplier.serializers import SupplierSerializer, PurchaseOrderSerializer, PurchaseOrderItemSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.core.decorators import check_role
from api.core.paginator import CustomPagination

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_list(request):
    search = request.GET.get('search')
    suppliers = Supplier.objects.all().order_by('id')
    if search:
        suppliers = suppliers.filter(
            Q(name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(email__icontains=search) |
            Q(contact_person__icontains=search)
        )

    paginator = CustomPagination()
    paginated_suppliers = paginator.paginate_queryset(suppliers, request)
    serializer = SupplierSerializer(paginated_suppliers, many=True)

    return Response({"message": "Successfully fetched all suppliers", 'pagination': paginator.get_paginated_response(),
                     "data": serializer.data}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_detail(request, supplier_id):
    try:
        supplier = Supplier.objects.get(pk=supplier_id)
    except Supplier.DoesNotExist:
        return Response({"message": "Supplier not found"}, status=404)
    serializer = SupplierSerializer(supplier)
    return Response({"message": "Successfully fetched supplier", "data": serializer.data}, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@check_role(['admin', 'manager'])
def create_supplier(request):
    serializer = SupplierSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Successfully created supplier", "data": serializer.data}, status=201)
    else:
        return Response({"message": serializer.errors}, status=400)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@check_role(['admin', 'manager'])
def update_supplier(request, supplier_id):
    if request.method == "PUT":
        try:
            supplier = Supplier.objects.get(pk=supplier_id)
            serializer = SupplierSerializer(supplier, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Successfully updated supplier", "data": serializer.data}, status=200)
            else:
                return Response({"message": serializer.errors}, status=400)
        except Supplier.DoesNotExist:
            return Response({"message": "Supplier not found"}, status=404)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
@check_role(['admin', 'manager'])
def delete_supplier(request, supplier_id):
    if request.method == "DELETE":
        try:
            supplier = Supplier.objects.get(pk=supplier_id)
            supplier.delete()
            return Response({"message": "Successfully deleted supplier", "data": supplier.name}, status=200)
        except Supplier.DoesNotExist:
            return Response({"message": "Supplier not found"}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def supplier_order_total(request, supplier_id):
    try:
        supplier = Supplier.objects.get(pk=supplier_id)
    except Supplier.DoesNotExist:
        return Response({"message": "Supplier not found"}, status=404)
    serializer = SupplierSerializer(supplier)
    total_order_amount = serializer.data['total_order_amount']
    total_paid_amount = serializer.data['total_paid_amount']
    total_due_amount = serializer.data['total_due_amount']
    return Response({"message": "Successfully fetched total order",
                     "data": {"total_order_amount": total_order_amount, "total_paid_amount": total_paid_amount,
                              "total_due_amount": total_due_amount}},
                    status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
def supplier_orders(request, supplier_id):
    try:
        orders = PurchaseOrder.objects.filter(supplier=supplier_id)
        serializer = PurchaseOrderSerializer(orders, many=True)
        return Response({"message": "Successfully fetched orders", "data": serializer.data}, status=200)
    except Supplier.DoesNotExist:
        return Response({"message": "Supplier not found or has no orders"}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def supplier_order_items(request, supplier_id):
    try:
        purchase_orders = PurchaseOrder.objects.filter(supplier_id=supplier_id)
        order_items = PurchaseOrderItem.objects.filter(purchase_order__in=purchase_orders)
        serializer = PurchaseOrderItemSerializer(order_items, many=True)
        return Response({"message": "Successfully fetched orders", "data": serializer.data}, status=200)
    except Supplier.DoesNotExist:
        return Response({"message": "Supplier not found"}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def supplier_products(request, supplier_id):
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        return Response({"message": "Supplier not found"}, status=404)

    search = request.GET.get('search', None)
    category = request.GET.get('category', None)
    subcategory = request.GET.get('subcategory', None)

    products = Product.objects.filter(supplier=supplier_id)

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
    data = serializer.data

    for product in data:
        product_image = product.get('product_image', '')
        if product_image.startswith('/media/http%3A'):
            fixed_url = product_image.replace('/media/http%3A', 'http:/')
            product['product_image'] = fixed_url

    return Response(
        {"message": "All products fetched successfully", 'pagination': paginator.get_paginated_response(),
         "data": data}, status=200)
