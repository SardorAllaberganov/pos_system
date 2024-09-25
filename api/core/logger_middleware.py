import logging
import json
import time


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

        start_time = time.time()

        # Log request details
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                request_body = json.loads(request.body.decode('utf-8'))
                request_body = sanitize_data(request_body)
            except json.JSONDecodeError:
                request_body = "Invalid JSON"
        else:
            request_body = {}

        logger.info("------------")
        logger.info("--REQUEST--")
        logger.info("------------")
        logger.info(f"URL: {request.build_absolute_uri()}")
        logger.info(f"HEADER: {dict(request.headers)}")
        logger.info(f"METHOD: {request.method}")
        logger.info(f"BODY: {request_body}")
        logger.info("------------")

        # Get the response
        response = self.get_response(request)
        end_time = time.time()
        duration = end_time - start_time
        duration = round(duration, 2)

        logger.info(f"--RESPONSE--")
        logger.info(f"------------")
        logger.info(f"DURATION: {duration}")
        logger.info(f"CODE: {response.status_code}")
        logger.info(f"RESPONSE HEADERS: {dict(response.items())}")

        # Log response details
        if hasattr(response, 'data'):  # For DRF Response
            response_body = sanitize_data(response.data)
            logger.info(f"BODY: {response_body}\n")
        else:
            logger.info(f"BODY: {response.content.decode('utf-8')}\n")

        return response
