"""
Synth-GPR: Synthetic GPR Data Generation Pipeline for Railway Ballast Fouling Detection

This package provides tools for generating synthetic GPR data, processing signals,
and extracting features for machine learning applications in railway engineering.
"""

# Import key modules for easy access
from .config import GeneratorConfig
from .constants import PC, MC, SC, PAC, PHC
from .logging_config import get_logger, setup_logging, quick_setup

# Package metadata
__version__ = "1.0.0"
__author__ = "Synth-GPR Team"
__description__ = "Synthetic GPR Data Generation Pipeline"

# Default logger
default_logger = get_logger(__name__)

__all__ = [
    'GeneratorConfig',
    'PC', 'MC', 'SC', 'PAC', 'PHC',
    'get_logger', 'setup_logging', 'quick_setup',
    'default_logger',
]