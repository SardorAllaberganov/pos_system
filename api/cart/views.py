from django.core.exceptions import MultipleObjectsReturned
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .serializers import CartSerializer, CartItemSerializer
from api.customer.models import Customer
from .models import Cart, CartItem
from ..product.models import Product


@api_view(["GET"])
@permission_classes([AllowAny])
def get_cart(request):
    customer = request.data.get("customer")
    try:
        cart = Cart.objects.get(customer=customer, is_active=True)
        cart_item = CartItem.objects.filter(cart=cart)
        serializer = CartSerializer(cart)
        serializer_item = CartItemSerializer(cart_item, many=True)

        return Response({"message": "All carts", "data": serializer.data, "cart_items": serializer_item.data},
                        status=200)
    except Cart.DoesNotExist:
        return Response({"error": "No active cart found"}, status=404)


@api_view(["POST"])
@permission_classes([AllowAny])
def add_to_cart(request):
    customer_id = request.data.get("customer_id")
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))
    try:
        product = Product.objects.get(id=product_id)
        customer = Customer.objects.get(id=customer_id)
    except Product.DoesNotExist:
        return Response({"error": "No product found"}, status=404)
    except Customer.DoesNotExist:
        return Response({"error": "No customer found"}, status=404)

    if quantity > product.quantity:
        return Response({"detail": f"Only {product.quantity} units available in stock."}, status=400)

    cart, created = Cart.objects.get_or_create(customer=customer, is_active=True)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product,
                                                        defaults={"quantity": quantity,
                                                                  'selling_price': product.selling_price})

    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.quantity:
            return Response({"detail": f"Cannot add more than {product.quantity} units in total."},
                            status=400)
        cart_item.quantity = new_quantity
        cart_item.save()

    serializer = CartItemSerializer(cart_item)
    return Response({"message": "Cart", "data": serializer.data}, status=200)


@api_view(["PUT"])
@permission_classes([AllowAny])
def update_cart(request, cart_item_id):
    try:
        cart_item = CartItem.objects.get(id=cart_item_id)
    except CartItem.DoesNotExist:
        return Response({"error": "No cart item found"}, status=404)

    quantity = int(request.data.get("quantity"))

    if quantity and quantity > 0:
        product = cart_item.product
        if quantity > product.quantity:
            return Response({"detail": f"Only {product.quantity} units available in stock."}, status=400)

        cart_item.quantity = quantity
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response({"message": "Cart", "data": serializer.data}, status=200)
    if quantity <= 0:
        cart_item.delete()
        return Response({"detail": "Item removed from cart"}, status=204)
    return Response({"error": "Invalid quantity"}, status=400)


@api_view(["DELETE"])
@permission_classes([AllowAny])
def remove_cart_item(request, cart_item_id):
    try:
        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.delete()
        return Response({"message": "Item removed from cart"}, status=204)
    except CartItem.DoesNotExist:
        return Response({"error": "No cart item found"}, status=404)


@api_view(["DELETE"])
@permission_classes([AllowAny])
def clear_cart(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id, is_active=True)
        cart.cart_items.all().delete()
        cart.delete()
        return Response({"message": "Cart cleared and deleted"}, status=204)
    except Cart.DoesNotExist:
        return Response({"error": "No active item found"}, status=404)
