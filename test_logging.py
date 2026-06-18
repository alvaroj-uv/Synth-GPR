#!/usr/bin/env python3
"""
Test script for the logging implementation.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('.'))

# Test 1: Import logging config
print("Test 1: Import logging configuration...")
try:
    from src.logging_config import setup_logging, get_logger, quick_setup
    print("✓ Successfully imported logging configuration")
except ImportError as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

# Test 2: Setup logging
print("\nTest 2: Setup logging...")
try:
    setup_logging(log_level='INFO')
    print("✓ Successfully setup logging")
except Exception as e:
    print(f"✗ Failed to setup logging: {e}")
    sys.exit(1)

# Test 3: Create logger
print("\nTest 3: Create logger...")
try:
    logger = get_logger('test_module')
    print("✓ Successfully created logger")
except Exception as e:
    print(f"✗ Failed to create logger: {e}")
    sys.exit(1)

# Test 4: Test logging levels
print("\nTest 4: Test logging levels...")
try:
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    print("✓ Successfully logged messages at all levels")
except Exception as e:
    print(f"✗ Failed to log messages: {e}")
    sys.exit(1)

# Test 5: Test src module imports
print("\nTest 5: Test src module imports...")
try:
    from src import get_logger as module_get_logger, setup_logging as module_setup
    print("✓ Successfully imported logging utilities from src module")
except ImportError as e:
    print(f"✗ Failed to import from src module: {e}")
    sys.exit(1)

# Test 6: Test script logging
print("\nTest 6: Test script logging...")
try:
    from scripts.script_logging import setup_script_logging, log, log_info, log_warning, log_error
    setup_script_logging(level='DEBUG')
    log("Test log message")
    log_info("Test info message")
    log_warning("Test warning message")
    log_error("Test error message")
    print("✓ Successfully tested script logging utilities")
except ImportError as e:
    print(f"✗ Failed to import script logging: {e}")
    print("  Note: This is expected if scripts/script_logging.py hasn't been imported yet")
except Exception as e:
    print(f"✗ Failed script logging test: {e}")

print("\n" + "="*50)
print("LOGGING IMPLEMENTATION TEST COMPLETED")
print("="*50)
print("\nSummary:")
print("- Created logging_config.py module")
print("- Updated src/__init__.py to expose logging utilities")
print("- Updated key source files (dataset_generator.py, data_loader.py, etc.)")
print("- Created script_logging.py for easy script usage")
print("- Updated example script (compare_synth_real_cutoff_interp.py)")
print("\nRemaining work:")
print("- Update remaining src files with print statements")
print("- Migrate print statements in other scripts as needed")
print("- Use the provided utilities as examples")