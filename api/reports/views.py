from django.db.models import Count, Sum, F
from rest_framework.response import Response
from api.sales.models import Sale, SaleItem
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def sales_reports(request):
    try:
        # Top 10 selling products
        top_selling_products = SaleItem.objects.values('product__name').annotate(
            total_quantity=Sum('quantity')).order_by('-total_quantity')[:10]

        # Total sales amount and peak sales times
        total_sales_amount = Sale.objects.aggregate(total=Sum('total_amount'))['total']
        peak_sales_times = Sale.objects.extra(select={'hour': "strftime('%%H', updated_at)"}).values('hour').annotate(
            total_sales=Sum('total_amount')
        ).order_by('-total_sales')

        # Sales trends by day
        sales_trends = Sale.objects.extra(select={'day': "strftime('%%Y-%%m-%%d', updated_at)"}).values('day').annotate(
            total_sales=Sum('total_amount')
        ).order_by('day')

        return Response({
            "top_selling_products": top_selling_products,
            "total_sales_amount": total_sales_amount,
            "peak_sales_times": peak_sales_times,
            "sales_trends": sales_trends,
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
