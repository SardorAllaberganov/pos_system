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


from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas

@api_view(["POST"])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def get_receipt(request, sale_id):
    try:
        receipt = Receipt.objects.get(sale__id=sale_id)
        serializer = ReceiptSerializer(receipt)
        print(serializer)
        return Response({"message": "Receipt successfully fetched", "data": serializer.data}, status=201)
    except Receipt.DoesNotExist:
        return Response({"message": "No receipt found"}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_receipt_pdf(request, receipt_number):
    try:
        receipt = Receipt.objects.get(receipt_number=receipt_number)
    except Receipt.DoesNotExist:
        return HttpResponse("Receipt not found.", status=404)

        # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.receipt_number}.pdf"'

    # Create a canvas object
    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Title of the receipt
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Receipt")

    # Sales information
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height - 100, f"Receipt Number: {receipt.receipt_number}")
    pdf.drawString(50, height - 120, f"Date: {receipt.created_at}")
    pdf.drawString(50, height - 140, f"Cashier: {receipt.cashier.name}")
    pdf.drawString(50, height - 160, f"Customer: {receipt.customer.name}")
    pdf.drawString(50, height - 180, f"Payment Type: {receipt.payment_type}")

    # Table for items
    items = [["Item", "Quantity", "Price", "Total"]]
    for item in receipt.sale.items.all():
        items.append([item.product, str(item.quantity), f"${item.selling_price:.2f}", f"${item.get_total_price:.2f}"])

    # Total amount
    items.append(["", "", "Total Amount:", f"${receipt.total_amount:.2f}"])

    # Create a table
    table = Table(items, colWidths=[50 * mm, 20 * mm, 40 * mm, 40 * mm])

    # Set table style (minimalist)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    # Position the table on the page
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, 50, height - 270)

    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(50, 50, "Thank you for your purchase!")

    # Finalize the PDF
    pdf.showPage()
    pdf.save()

    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
