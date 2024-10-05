import os
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

class Logger(object):
    def __init__(self, log_type):
        self.log_type = log_type
        self.logger = self.setup_logger()

    def setup_logger(self):
        """Sets up the logger with the correct handler and configuration."""
        logger = logging.getLogger(self.log_type)
        logger.setLevel(logging.INFO)

        # Avoid adding duplicate handlers
        if not logger.hasHandlers():
            # Set up the handler for this logger
            handler = self.handler(self.file_name())
            logger.addHandler(handler)

        return logger

    def file_name(self):
        """Generates the file path based on log type and current time."""
        current_time = datetime.now()
        day_folder = current_time.strftime("%d-%m-%Y")
        hour_folder = current_time.strftime("%H-00")

        # Define the log file path
        log_dir = f'logs/{day_folder}/{hour_folder}'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        return f'{log_dir}/{hour_folder}-{self.log_type}.log'

    def handler(self, log_file):
        """Creates a TimedRotatingFileHandler for the logger."""
        handler = TimedRotatingFileHandler(log_file, when='H', interval=1, backupCount=0)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        return handler

    def log_info(self, message):
        """Logs an informational message."""
        self.logger.info(message)

    def log_exception(self, message):
        """Logs an exception message."""
        self.logger.exception(message)
