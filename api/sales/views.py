from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes, api_view
from decimal import Decimal
from api.cart.models import Cart
from .models import Sale, SaleItem, Receipt
from .serializers import SaleSerializer, ReceiptSerializer
from api.customer.models import Customer
from api.core.paginator import CustomPagination
from django.db.models import Q
from datetime import datetime
from django.utils.dateparse import parse_date

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas

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

@api_view(['GET'])
@permission_classes([AllowAny])
def get_receipt(request, sale_id):
    try:
        receipt = Receipt.objects.get(sale__id=sale_id)
        serializer = ReceiptSerializer(receipt)
        print(serializer)
        return Response({"message": "Receipt successfully fetched", "data": serializer.data}, status=201)
    except Receipt.DoesNotExist:
        return Response({"message": "No receipt found"}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_receipt_pdf(request, receipt_number):
    try:
        receipt = Receipt.objects.get(receipt_number=receipt_number)
    except Receipt.DoesNotExist:
        return HttpResponse("Receipt not found.", status=404)

        # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.receipt_number}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter  # Set page size

    # Add a logo (optional)
    # p.drawImage("path/to/logo.png", 50, 700, width=100, height=50)  # Uncomment to add a logo

    # Draw header
    p.setFillColor(colors.lightgrey)
    p.rect(50, 740, 500, 50, fill=1)  # Header background
    p.setFont('Helvetica-Bold', 24)
    p.setFillColor(colors.black)
    p.drawString(250, 760, "Receipt")

    # Draw receipt details
    p.setFont('Helvetica', 12)
    y_position = 700
    p.drawString(100, y_position, f"Receipt Number: {receipt.receipt_number}")
    y_position -= 20
    p.drawString(100, y_position, f"Cashier: {receipt.cashier.name}")
    y_position -= 20
    p.drawString(100, y_position, f"Customer: {receipt.customer.name}")
    y_position -= 20
    p.drawString(100, y_position, f"Created At: {receipt.created_at}")
    y_position -= 20
    p.drawString(100, y_position, f"Total Amount: ${receipt.total_amount:.2f}")
    y_position -= 20
    p.drawString(100, y_position, f"Payment Type: {receipt.payment_type}")

    # Draw a line to separate sections
    p.setStrokeColor(colors.black)
    p.line(100, y_position - 10, 500, y_position - 10)

    # Prepare items data for the table
    items_data = [["Product", "Quantity", "Price"]]
    for item in receipt.sale.items.all():
        items_data.append([item.product, str(item.quantity), f"${item.selling_price:.2f}"])

    # Create a table for items
    table = Table(items_data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    # Draw the table
    table.wrapOn(p, width, height)
    table.drawOn(p, 100, y_position - 60)  # Adjust position as needed

    # Finalize the PDF
    p.showPage()
    p.save()

    return response

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_sales(request):
    search = request.GET.get('search')

    sales = Sale.objects.all()

    if search:
        sales = sales.filter(
            Q(id__icontains=search) |
            Q(payment_status__icontains=search) |
            Q(customer__id__icontains=search) |
            Q(cashier__name__icontains=search) |
            Q(payment_type__icontains=search)
        )

    paginator = CustomPagination()
    paginated_sales = paginator.paginate_queryset(sales, request)
    serializer = SaleSerializer(paginated_sales, many=True)
    data = serializer.data
    return Response(
        {"message": "All sales fetched successfully", "pagination": paginator.get_paginated_response(), "data": data},
        status=200)
