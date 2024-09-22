from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes, api_view

from api.cart.models import Cart
from .models import Sale, SaleItem
from .serializers import SaleSerializer
from api.customer.models import Customer

@api_view(["POST"])
@permission_classes([AllowAny])
def checkout_cart(request):
    customer_id = request.data.get("customer_id")
    try:
        cart = Cart.objects.get(customer=customer_id, is_active=True)
        customer = Customer.objects.get(pk=customer_id)
        total_amount = sum(item.quantity * item.product.selling_price for item in cart.cart_items.all())
        sale = Sale.objects.create(
            cashier=request.user,
            customer=customer,
            total_amount=total_amount,
            payment_status="completed"
        )
        for cart_item in cart.cart_items.all():
            SaleItem.objects.create(
                sale=sale,
                product=cart_item.product,
                quantity=cart_item.quantity,
                selling_price=cart_item.product.selling_price
            )
        cart.cart_items.all().delete()
        cart.is_active = False
        cart.delete()
        cart.save()
        serializer = SaleSerializer(sale)
        return Response({"message": "Sale successfully created", "data": serializer.data}, status=201)
    except Cart.DoesNotExist:
        return Response({"message": "No active cart found"}, status=404)
