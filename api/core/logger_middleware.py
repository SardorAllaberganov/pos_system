import logging
import json
from time import time
from django.utils.deprecation import MiddlewareMixin
import os
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger('api_logger')
SENSITIVE_FIELDS = ['password', 'token']

BASE_LOGS_DIR = getattr(settings, 'BASE_LOGS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'))


def sanitize_data(data):
    """
    Obfuscate sensitive fields in the logged data.
    """
    for field in SENSITIVE_FIELDS:
        if field in data:
            data[field] = '********'
    return data


class APILoggingMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        request.start_time = time()

        now = timezone.localtime()
        date_str = now.strftime('%d-%m-%Y')
        hour_str = now.strftime('%H-00')

        # Build the dynamic path for the log file
        log_dir = os.path.join(BASE_LOGS_DIR, date_str, hour_str)
        os.makedirs(log_dir, exist_ok=True)

        log_filename = os.path.join(log_dir, f"{date_str}_{hour_str}_api_requests.log")

        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()

        # Create a new file handler dynamically for the request
        file_handler = logging.FileHandler(filename=log_filename)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Add the new file handler to the logger
        logger.addHandler(file_handler)

        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                request_body = json.loads(request.body.decode('utf-8'))
                request_body = sanitize_data(request_body)
            except json.JSONDecodeError:
                request_body = "Invalid JSON"
        else:
            request_body = {}

        # Log the request details
        message = (
            f"\n------------\n"
            f"--REQUEST--\n"
            f"------------\n"
            f"URL: {request.build_absolute_uri()}\n"
            f"HEADER: {dict(request.headers)}\n"
            f"METHOD: {request.method}\n"
            f"BODY: {request_body}\n"
            f"------------"
        )
        logger.info(message)

    @staticmethod
    def process_response(request, response):
        end_time = time()
        if hasattr(response, 'data'):  # For DRF Response
            response_body = sanitize_data(response.data)
        else:
            logger.info(f"Response Body: {response.content.decode('utf-8')}")

        duration = end_time - request.start_time

        message = (
            f"------------\n"
            f"--RESPONSE--\n"
            f"------------\n"
            f"DURATION: {duration:.2f} seconds\n"
            f"STATUS: {response.status_code}\n"
            f"RESPONSE BODY: {response_body}\n"
            f"------------\n"
        )
        logger.info(message)
        logger.handlers.clear()

        return response
