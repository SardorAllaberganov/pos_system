from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Customer
from .serializers import CustomerSerializer
from django.db.models import Q
from api.core.paginator import CustomPagination


@api_view(['GET'])
@permission_classes([AllowAny])
def all_customers(request):
    search = request.GET.get('search', None)
    customers = Customer.objects.all()

    if search:
        customers = customers.filter(
            Q(name__icontains=search) | Q(email__icontains=search) | Q(phone_number__icontains=search))

    paginator = CustomPagination()
    paginated_customers = paginator.paginate_queryset(customers, request)

    serializer = CustomerSerializer(paginated_customers, many=True)
    return Response({"message": "Successfully fetched all customers", "data": serializer.data}, status=200)
