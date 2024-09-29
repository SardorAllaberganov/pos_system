from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Customer
from .serializers import CustomerSerializer
from django.db.models import Q
from api.core.paginator import CustomPagination

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_detail(request, customer_id):
    try:
        customer = Customer.objects.get(pk=customer_id)
    except Customer.DoesNotExist:
        return Response({"message": "Customer not found"}, status=404)

    serializer = CustomerSerializer(customer)
    return Response({"message": "Successfully fetched customer", "data": serializer.data}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_customer(request):
    if request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Customer created", "data": serializer.data}, status=201)
        else:
            return Response({"error": serializer.errors}, status=400)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_customer(request, customer_id):
    if request.method == 'PUT':
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return Response({"message": "Customer not found"}, status=404)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Successfully updated customer", "data": serializer.data}, status=200)
        else:
            return Response({"error": serializer.errors}, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_customer(request, customer_id):
    try:
        customer = Customer.objects.get(pk=customer_id)
        customer.delete()
        return Response({"message": "Customer deleted", "data": None}, status=200)
    except Customer.DoesNotExist:
        return Response({"message": "Customer not found"}, status=404)
