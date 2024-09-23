from rest_framework.decorators import api_view
from rest_framework.response import Response
from functools import wraps


def check_role(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({'error': "Authentication required"}, status=401)
            if request.user.role not in roles:
                return Response({
                                    'error': f"Permission denied. Only {", ".join(roles) if len(roles) > 1 else roles[0]} can perform this action"},
                                status=403)
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
