"""
Script logging utilities for Synth-GPR.

This module provides simple logging setup for Python scripts that don't want
to deal with complex logging configuration.

Usage in scripts:
    from script_logging import setup_script_logging, log
    
    # Basic setup (defaults to INFO level, console output)
    setup_script_logging()
    
    # Then use log() function instead of print()
    log("Processing started...")
    log(f"Found {count} files", level="warning")
    log(f"Error: {error}", level="error")
    
    # Or use the logger directly
    from script_logging import logger
    logger.info("Detailed info message")
    logger.error("Error message")
"""

import logging
import sys
from typing import Optional, Union


# Create script logger
logger = logging.getLogger('script')


def setup_script_logging(
    level: Union[str, int] = logging.INFO,
    log_file: Optional[str] = None,
    format_style: str = 'simple'
) -> logging.Logger:
    """
    Setup logging for a script.
    
    Args:
        level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR') or int
        log_file: Optional path to log file
        format_style: 'simple' or 'detailed'
        
    Returns:
        Configured logger instance
    """
    # Convert string level to int
    if isinstance(level, str):
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        level = level_map.get(level.upper(), logging.INFO)
    
    # Configure logger
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Select format
    if format_style == 'detailed':
        log_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    else:
        log_format = '%(levelname)-8s | %(message)s'
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        from pathlib import Path
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
        ))
        logger.addHandler(file_handler)
    
    return logger


def log(message: str, level: str = 'info', logger_name: Optional[str] = None) -> None:
    """
    Simple logging function as a replacement for print().
    
    Args:
        message: Message to log
        level: Log level ('debug', 'info', 'warning', 'error', 'critical')
        logger_name: Optional logger name (defaults to 'script')
    """
    log_levels = {
        'debug': logger.debug,
        'info': logger.info,
        'warning': logger.warning,
        'error': logger.error,
        'critical': logger.critical,
    }
    
    log_func = log_levels.get(level.lower(), logger.info)
    log_func(message)


# Initialize with basic setup
setup_script_logging()


# Convenience aliases for common logging patterns
def log_info(message: str) -> None:
    """Log an info message."""
    logger.info(message)


def log_warning(message: str) -> None:
    """Log a warning message."""
    logger.warning(message)


def log_error(message: str) -> None:
    """Log an error message."""
    logger.error(message)


def log_debug(message: str) -> None:
    """Log a debug message."""
    logger.debug(message)


def log_success(message: str) -> None:
    """Log a success message with visual emphasis."""
    logger.info(f"✓ {message}")


def log_header(title: str, char: str = '=') -> None:
    """Log a section header."""
    logger.info(f"\n{char * 70}")
    logger.info(f"{title}")
    logger.info(char * 70)


def log_separator(char: str = '-') -> None:
    """Log a separator line."""
    logger.info(char * 70)