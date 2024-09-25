import logging
import json

logger = logging.getLogger('api_logger')
SENSITIVE_FIELDS = ['password', 'token']


def sanitize_data(data):
    """
    Obfuscate sensitive fields in the logged data.
    """
    for field in SENSITIVE_FIELDS:
        if field in data:
            data[field] = '********'
    return data


class APILoggingMiddleware:
    """
    Middleware for logging all API requests and responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                request_body = json.loads(request.body.decode('utf-8'))
                request_body = sanitize_data(request_body)
            except json.JSONDecodeError:
                request_body = "Invalid JSON"
        else:
            request_body = {}

        logger.info(f"Request Method: {request.method}")
        logger.info(f"Request URL: {request.build_absolute_uri()}")
        logger.info(f"Request Headers: {dict(request.headers)}")
        logger.info(f"Request Body: {request_body}")

        # Get the response
        response = self.get_response(request)

        # Log response details
        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.items())}")
        if hasattr(response, 'data'):  # For DRF Response
            response_body = sanitize_data(response.data)
            logger.info(f"Response Body: {response_body}")
        else:
            logger.info(f"Response Body: {response.content.decode('utf-8')}")

        return response
