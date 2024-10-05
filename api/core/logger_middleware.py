# import logging
# import json
# from time import time
# from django.utils.deprecation import MiddlewareMixin
# import os
# from django.utils import timezone
# from django.conf import settings
#
# logger = logging.getLogger('api_logger')
# SENSITIVE_FIELDS = ['password', 'token']
#
# BASE_LOGS_DIR = getattr(settings, 'BASE_LOGS_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'))
#
#
# def sanitize_data(data):
#     """
#     Obfuscate sensitive fields in the logged data.
#     """
#     for field in SENSITIVE_FIELDS:
#         if field in data:
#             data[field] = '********'
#     return data
#
#
# class APILoggingMiddleware(MiddlewareMixin):
#     @staticmethod
#     def process_request(request):
#         request.start_time = time()
#
#         now = timezone.localtime()
#         date_str = now.strftime('%d-%m-%Y')
#         hour_str = now.strftime('%H-00')
#
#         # Build the dynamic path for the log file
#         log_dir = os.path.join(BASE_LOGS_DIR, date_str, hour_str)
#         os.makedirs(log_dir, exist_ok=True)
#
#         log_filename = os.path.join(log_dir, f"{date_str}_{hour_str}_api_requests.log")
#
#         # Clear existing handlers to avoid duplicates
#         logger.handlers.clear()
#
#         # Create a new file handler dynamically for the request
#         file_handler = logging.FileHandler(filename=log_filename)
#         file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
#
#         logger.addHandler(file_handler)
#
#         if request.method in ['POST', 'PUT', 'PATCH']:
#             try:
#                 request_body = json.loads(request.body.decode('utf-8'))
#                 request_body = sanitize_data(request_body)
#             except json.JSONDecodeError:
#                 request_body = "Invalid JSON"
#         else:
#             request_body = request.body.decode('utf-8', errors='replace')
#
#         message = (
#             f"\n------------\n"
#             f"--REQUEST--\n"
#             f"------------\n"
#             f"URL: {request.build_absolute_uri()}\n"
#             f"HEADER: {dict(request.headers)}\n"
#             f"METHOD: {request.method}\n"
#             f"REQUEST BODY: {request_body}\n"
#             f"------------"
#         )
#         logger.info(message)
#
#     @staticmethod
#     def process_response(request, response):
#         end_time = time()
#         if hasattr(response, 'data'):  # For DRF Response
#             response_body = sanitize_data(response.data)
#         else:
#             response_body = response.content.decode('utf-8', errors='replace')
#
#         duration = end_time - request.start_time
#
#         message = (
#             f"\n------------\n"
#             f"--RESPONSE--\n"
#             f"------------\n"
#             f"DURATION: {duration:.2f} seconds\n"
#             f"STATUS: {response.status_code}\n"
#             f"RESPONSE BODY: {response_body}\n"
#             f"------------\n"
#         )
#         logger.info(message)
#         logger.handlers.clear()
#
#         return response


import time

from django.utils.deprecation import MiddlewareMixin
from . import logger
from .logger import Logger
from django.http import FileResponse, StreamingHttpResponse

class APILoggerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """Log the API request details."""
        request.start_time = time.time()
        # Cache request body to avoid RawPostDataException
        if request.method in ('POST', 'PUT', 'PATCH'):
            request.body_data = self.get_request_body(request)

    def process_response(self, request, response):
        """Log the API request and response details after processing the request."""
        self.api_request(request, response)
        return response

    def process_exception(self, request, exception):
        """Log the exception details when an error occurs during request processing."""
        self.exception_log(request, exception)
        return None

    def get_request_body(self, request):
        """Safely get and cache the request body to prevent reading it multiple times."""
        try:
            body = request.body.decode('utf-8')
        except Exception as e:
            body = None
        return body

    def api_request(self, request, response):
        """Handles logging of API request and response."""
        # Set up the logger for API requests
        logger = Logger(log_type='api_request')

        # Calculate request duration
        duration = time.time() - request.start_time

        # Capture request details
        request_data = {
            'url': request.build_absolute_uri(),
            'method': request.method,
            'headers': dict(request.headers),
            'body': getattr(request, 'body_data', None),
        }

        if isinstance(response, (FileResponse, StreamingHttpResponse)):
            logger.log_info("Skipping logging of file/streaming response content.")
        else:
            # Try to log the response content, but handle missing content attributes gracefully
            try:
                logger.log_info(f"Response Content: {response.content}")
            except AttributeError:
                logger.log_info("Response has no 'content' attribute, skipping content logging.")

        response_data = {
            'status_code': response.status_code,
            'duration': f'{duration:.2f}ms',
        }

        # Log both request and response
        logger.log_info(f"Request: {request_data}")
        logger.log_info(f"Response: {response_data}")

    def exception_log(self, request, exception):
        """Handles logging of exceptions during request processing."""
        # Set up the logger for exceptions
        logger = Logger(log_type='error_logs')

        # Calculate the duration before the exception occurred
        duration = time.time() - request.start_time

        # Capture the exception details
        exception_data = {
            'url': request.build_absolute_uri(),
            'duration': duration,
            'message': str(exception),
        }

        # Log the exception
        logger.log_exception(f"Exception: {exception_data}")
