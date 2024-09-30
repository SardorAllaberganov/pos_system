from django.db.models import Count, Sum, F, FloatField, ExpressionWrapper
from rest_framework.response import Response
from api.sales.models import Sale, SaleItem
from api.product.models import Product
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.core.decorators import check_role
from django.utils import timezone


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_reports(request):
    try:
        # Top 10 selling products
        top_selling_products = SaleItem.objects.values('product__name', 'sale__total_amount').annotate(
            total_quantity=Sum('quantity')).order_by('-total_quantity')[:3]

        # Total sales amount and peak sales times
        total_sales_amount = Sale.objects.aggregate(total=Sum('total_amount'))['total']
        sales = Sale.objects.all()
        peak_sales_times = {}
        for sale in sales:
            localtime = timezone.localtime(sale.updated_at)
            hour = localtime.strftime('%H:00')
            if hour not in peak_sales_times:
                peak_sales_times[hour] = 0
            peak_sales_times[hour] += sale.total_amount

        sorted_peak_sales = sorted(peak_sales_times.items(), key=lambda x: x[1], reverse=True)[:5]

        # Sales trends by day
        sales_trends = Sale.objects.extra(select={'day': "strftime('%%Y-%%m-%%d', updated_at)"}).values('day').annotate(
            total_sales=Sum('total_amount')
        ).order_by('day')[:5]

        return Response({
            "top_selling_products": top_selling_products,
            "total_sales_amount": total_sales_amount,
            "peak_sales_times": sorted_peak_sales,
            "sales_trends": sales_trends,
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_reports(request):
    try:
        # Low stock items (restock needed)
        low_stock_products = Product.objects.filter(quantity__lte=20).annotate(
            category_name=F('subcategory__category__name')
        ).values(
            'name', 'quantity', 'selling_price', 'category_name'
        )
        # Product turnover rate (sales vs stock)
        sale_items = SaleItem.objects.values('product__id', 'product__name').annotate(
            total_sold=Sum('quantity')
        )

        product_data = []
        for item in sale_items:
            product_id = item['product__id']
            product = Product.objects.get(id=product_id)
            total_sold = item['total_sold']
            current_stock = product.quantity
            total_handled = total_sold + current_stock
            turnover_rate = total_sold / total_handled if total_handled > 0 else 0

            product_data.append({
                'product_id': product_id,
                'product_name': item['product__name'],
                'total_sold': total_sold,
                'current_stock': current_stock,
                'turnover_rate': round(turnover_rate, 2)
            })

        return Response({
            "low_stock_products": low_stock_products,
            "product_turnover": product_data,
        }, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_reports(request):
    try:
        # Customer purchase frequency
        customer_purchase_frequency = Sale.objects.values('customer__name').annotate(
            total_purchases=Count('id')
        ).order_by('-total_purchases')

        # Average order value
        average_order_value = Sale.objects.aggregate(avg_value=Sum('total_amount') / Count('id'))['avg_value']

        # Customer lifetime value
        customer_lifetime_value = Sale.objects.values('customer__name').annotate(
            lifetime_value=Sum('total_amount')
        ).order_by('-lifetime_value')

        return Response({
            "customer_purchase_frequency": customer_purchase_frequency,
            "average_order_value": average_order_value,
            "customer_lifetime_value": customer_lifetime_value,
        }, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@check_role(['admin', 'manager'])
def employee_performance_reports(request):
    try:
        # Employee performance based on total sales
        employee_performance = Sale.objects.values('cashier__name').annotate(
            total_sales=Sum('total_amount')
        ).order_by('-total_sales')

        return Response({
            "employee_performance": employee_performance,
        }, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
