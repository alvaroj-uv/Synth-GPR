"""
Logging configuration for Synth-GPR pipeline.

This module provides centralized logging configuration and utilities
for the synthetic GPR data generation pipeline.

Usage:
    from src.logging_config import get_logger, setup_logging
    
    # Basic usage in modules
    logger = get_logger(__name__)
    logger.info("Processing started")
    logger.debug("Detailed debug information")
    logger.warning("Something unusual happened")
    logger.error("An error occurred")
    
    # In main scripts
    setup_logging(log_level=logging.INFO)
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Union


# Define log levels for different contexts
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

# Default log level
DEFAULT_LOG_LEVEL = logging.INFO

# Log format
LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
LOG_FORMAT_SIMPLE = '%(levelname)-8s | %(name)s | %(message)s'
LOG_FORMAT_DETAILED = '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s'

# Log directory
LOG_DIR = Path('logs')


class SynthGPRFormatter(logging.Formatter):
    """Custom formatter for Synth-GPR logging."""
    
    def format(self, record):
        # Add custom formatting for specific log levels
        if record.levelno >= logging.ERROR:
            # Bold red for errors
            levelname = f'\033[1;31m{record.levelname}\033[0m' if sys.stdout.isatty() else record.levelname
        elif record.levelno >= logging.WARNING:
            # Yellow for warnings
            levelname = f'\033[1;33m{record.levelname}\033[0m' if sys.stdout.isatty() else record.levelname
        elif record.levelno <= logging.DEBUG:
            # Cyan for debug
            levelname = f'\033[1;36m{record.levelname}\033[0m' if sys.stdout.isatty() else record.levelname
        else:
            # Green for info
            levelname = f'\033[1;32m{record.levelname}\033[0m' if sys.stdout.isatty() else record.levelname
        
        # Use parent formatting
        record.levelname = levelname
        return super().format(record)


def get_logger(name: str, log_level: Optional[int] = None) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        log_level: Optional log level override
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if log_level is not None:
        logger.setLevel(log_level)
    
    return logger


def setup_logging(
    log_level: Union[str, int] = DEFAULT_LOG_LEVEL,
    log_file: Optional[str] = None,
    console_output: bool = True,
    file_output: bool = False,
    format_style: str = 'standard',
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Configure logging for the Synth-GPR pipeline.
    
    Args:
        log_level: Logging level (string or int). Default: INFO
        log_file: Optional log file path. If None, uses logs/synth_gpr.log
        console_output: Whether to output to console
        file_output: Whether to output to file
        format_style: 'standard', 'simple', or 'detailed'
        max_bytes: Max log file size before rotation
        backup_count: Number of backup log files to keep
    """
    # Convert string level to int if needed
    if isinstance(log_level, str):
        log_level = LOG_LEVELS.get(log_level.upper(), DEFAULT_LOG_LEVEL)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Select format
    if format_style == 'simple':
        formatter = logging.Formatter(LOG_FORMAT_SIMPLE)
    elif format_style == 'detailed':
        formatter = SynthGPRFormatter(LOG_FORMAT_DETAILED)
    else:
        formatter = SynthGPRFormatter(LOG_FORMAT)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if file_output:
        # Create log directory if it doesn't exist
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        if log_file is None:
            log_file = LOG_DIR / 'synth_gpr.log'
        else:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Use rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set levels for noisy libraries (optional)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('numpy').setLevel(logging.WARNING)
    logging.getLogger('scipy').setLevel(logging.WARNING)
    logging.getLogger('h5py').setLevel(logging.WARNING)
    logging.getLogger('pymunk').setLevel(logging.WARNING)


def get_console_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a simple console logger without file output.
    
    Useful for scripts that only need console output.
    
    Args:
        name: Logger name
        level: Log level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Ensure console handler exists
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = SynthGPRFormatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def log_to_file(logger: logging.Logger, log_file: str, level: int = logging.INFO) -> logging.FileHandler:
    """
    Add file output to an existing logger.
    
    Args:
        logger: Logger instance
        log_file: Path to log file
        level: Log level for file output
        
    Returns:
        FileHandler instance
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    logger.addHandler(file_handler)
    
    return file_handler


# Convenience function for quick logging in scripts
def quick_setup(
    level: Union[str, int] = 'INFO',
    name: str = 'synth_gpr'
) -> logging.Logger:
    """
    Quick setup for simple scripts.
    
    Args:
        level: Log level
        name: Logger name
        
    Returns:
        Configured logger
    """
    if isinstance(level, str):
        level = LOG_LEVELS.get(level.upper(), DEFAULT_LOG_LEVEL)
    
    setup_logging(log_level=level, console_output=True, file_output=False)
    return get_logger(name, level)


# Module-level logger for this module
logger = get_logger(__name__)