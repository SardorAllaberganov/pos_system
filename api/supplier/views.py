from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from api.supplier.models import Supplier, PurchaseOrder, PurchaseOrderItem
from api.supplier.serializers import SupplierSerializer, PurchaseOrderSerializer, PurchaseOrderItemSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.core.decorators import check_role


@api_view(['GET'])
@permission_classes([AllowAny])
def supplier_list(request):
    suppliers = Supplier.objects.all()
    serializer = SupplierSerializer(suppliers, many=True)
    return Response({"message": "Successfully fetched all suppliers", "data": serializer.data}, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def supplier_detail(request, supplier_id):
    try:
        supplier = Supplier.objects.get(pk=supplier_id)
    except Supplier.DoesNotExist:
        return Response({"message": "Supplier not found"}, status=404)
    serializer = SupplierSerializer(supplier, many=True)
    return Response({"message": "Successfully fetched supplier", "data": serializer.data}, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@check_role(['Admin', 'Manager'])
def create_supplier(request):
    serializer = SupplierSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Successfully created supplier", "data": serializer.data}, status=201)
    else:
        return Response({"message": serializer.errors}, status=400)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@check_role(['Admin', 'Manager'])
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
@check_role(['Admin', 'Manager'])
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
        orders = PurchaseOrder.all_orders.filter(supplier=supplier_id)
        serializer = PurchaseOrderSerializer(orders, many=True)
        return Response({"message": "Successfully fetched orders", "data": serializer.data}, status=200)
    except Supplier.DoesNotExist:
        return Response({"message": "Supplier not found or has no orders"}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def supplier_order_items(request, supplier_id):
    try:
        purchase_orders = PurchaseOrder.all_orders.filter(supplier_id=supplier_id)
        order_items = PurchaseOrderItem.objects.filter(purchase_order__in=purchase_orders)
        serializer = PurchaseOrderItemSerializer(order_items, many=True)
        return Response({"message": "Successfully fetched orders", "data": serializer.data}, status=200)
    except Supplier.DoesNotExist:
        return Response({"message": "Supplier not found"}, status=404)
