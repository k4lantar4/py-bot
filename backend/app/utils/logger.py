"""
Logger utility for the 3X-UI Management System.

This module provides a configured logger for the application.
"""

import logging
import sys
from typing import Any, Dict, Optional

from app.core.config import settings


class Logger:
    """
    Logger class for the application.
    
    This class provides a configured logger with formatting and handlers.
    """
    
    def __init__(self, name: str = "app"):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
        
        # Set propagate to False to avoid duplicate logs
        self.logger.propagate = False
    
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a debug message.
        
        Args:
            msg: Message to log
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log an info message.
        
        Args:
            msg: Message to log
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a warning message.
        
        Args:
            msg: Message to log
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log an error message.
        
        Args:
            msg: Message to log
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a critical message.
        
        Args:
            msg: Message to log
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.critical(msg, *args, **kwargs)
    
    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log an exception message.
        
        Args:
            msg: Message to log
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.exception(msg, *args, **kwargs)


# Create a logger instance
logger = Logger() 