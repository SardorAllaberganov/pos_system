from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes, api_view
from decimal import Decimal
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
        payment_type = request.data.get("payment_type")
        loyalty_points_used = Decimal(request.data.get("loyalty_points_used", 0))
        total_amount = sum(item.quantity * item.product.selling_price for item in cart.cart_items.all())

        payment_amount = total_amount

        if loyalty_points_used > 0:
            if customer.loyalty_points >= loyalty_points_used:
                payment_amount -= loyalty_points_used
            else:
                return Response({"message": "Not enough loyalty points"}, status=400)

        sale = Sale.objects.create(
            cashier=request.user,
            customer=customer,
            total_amount=total_amount,
            loyalty_points_used=loyalty_points_used,
            payment_status="completed",
            payment_type=payment_type
        )
        for cart_item in cart.cart_items.all():
            SaleItem.objects.create(
                sale=sale,
                product=cart_item.product,
                quantity=cart_item.quantity,
                selling_price=cart_item.product.selling_price
            )
        cart.cart_items.all().delete()
        cart.delete()
        customer.loyalty_points -= loyalty_points_used
        customer.save()
        serializer = SaleSerializer(sale)
        return Response({"message": "Sale successfully created", "data": serializer.data}, status=201)
    except Cart.DoesNotExist:
        return Response({"message": "No active cart found"}, status=404)
