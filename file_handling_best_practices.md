# File Handling Best Practices for Python Applications

## Table of Contents

1. [General File Handling Principles](#general-file-handling-principles)
2. [Path Management](#path-management)
3. [File Reading Best Practices](#file-reading-best-practices)
4. [File Writing Best Practices](#file-writing-best-practices)
5. [Error Handling and Validation](#error-handling-and-validation)
6. [Security Considerations](#security-considerations)
7. [Performance Optimization](#performance-optimization)
8. [Testing Strategies](#testing-strategies)
9. [Logging and Monitoring](#logging-and-monitoring)
10. [File Format Specifics](#file-format-specifics)
11. [Advanced Patterns](#advanced-patterns)
12. [Synth-GPR Specific Recommendations](#synth-gpr-specific-recommendations)

## General File Handling Principles

### 1. Use Context Managers

**Best Practice**: Always use `with` statements for file operations to ensure proper resource cleanup.

```python
# GOOD: Context manager ensures file is closed
with open('file.txt', 'r') as f:
    content = f.read()

# BAD: Manual file management
f = open('file.txt', 'r')
content = f.read()
f.close()  # Easy to forget
```

**Benefits**:
- Automatic file closing even if exceptions occur
- Cleaner code with less boilerplate
- Prevents resource leaks

### 2. Prefer Pathlib Over os.path

**Best Practice**: Use `pathlib.Path` instead of `os.path` for path manipulation.

```python
# GOOD: Modern pathlib approach
from pathlib import Path
file_path = Path('data') / 'config' / 'settings.json'

# BAD: Legacy os.path approach
import os
file_path = os.path.join('data', 'config', 'settings.json')
```

**Benefits**:
- Object-oriented interface
- Cross-platform compatibility
- Built-in path validation
- Method chaining

### 3. Explicit Encoding

**Best Practice**: Always specify encoding explicitly (typically 'utf-8').

```python
# GOOD: Explicit encoding
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# BAD: Implicit encoding (platform-dependent)
with open('file.txt', 'r') as f:
    content = f.read()
```

**Common Encodings**:
- `'utf-8'`: Default for most applications
- `'utf-8-sig'`: UTF-8 with BOM
- `'latin-1'`: For legacy systems
- `'ascii'`: For ASCII-only files

### 4. Binary vs Text Mode

**Best Practice**: Choose the correct mode for your data type.

```python
# Text mode (default)
with open('text.txt', 'r', encoding='utf-8') as f:  # Text
    text = f.read()

# Binary mode
with open('image.png', 'rb') as f:  # Binary
    data = f.read()
```

**Mode Summary**:
- `'r'`: Read text (default)
- `'rb'`: Read binary
- `'w'`: Write text (truncates)
- `'wb'`: Write binary (truncates)
- `'a'`: Append text
- `'ab'`: Append binary
- `'r+'`: Read/write text
- `'rb+'`: Read/write binary

## Path Management

### 1. Absolute vs Relative Paths

**Best Practice**: Use absolute paths in production, relative paths in configuration.

```python
# GOOD: Resolve to absolute path
config_dir = Path(__file__).parent / 'config'
config_path = config_dir / 'settings.json'

# BAD: Relative path without context
config_path = Path('config/settings.json')
```

### 2. Path Construction

**Best Practice**: Build paths using pathlib operations.

```python
# GOOD: Path construction
base_dir = Path.home() / 'project'
data_dir = base_dir / 'data' / 'raw'
output_file = data_dir / f'results_{timestamp}.csv'

# BAD: String concatenation
output_file = 'data/raw/results_' + timestamp + '.csv'
```

### 3. Path Validation

**Best Practice**: Validate paths before operations.

```python
# GOOD: Path validation
def validate_path(path: Path, must_exist: bool = False):
    if not isinstance(path, Path):
        raise TypeError(f'Expected Path, got {type(path)}')
    
    if must_exist and not path.exists():
        raise FileNotFoundError(f'Path does not exist: {path}')
    
    if must_exist and not path.is_file():
        raise ValueError(f'Path is not a file: {path}')
    
    return path
```

### 4. Path Normalization

**Best Practice**: Normalize paths to handle `.` and `..`.

```python
# GOOD: Path normalization
raw_path = Path('data/../config/./settings.json')
normalized = raw_path.resolve()  # /absolute/path/config/settings.json

# BAD: Using unnormalized paths
with open(raw_path, 'r') as f:  # May cause issues
    pass
```

## File Reading Best Practices

### 1. Chunked Reading for Large Files

**Best Practice**: Read files in chunks to avoid memory issues.

```python
# GOOD: Chunked reading
CHUNK_SIZE = 8192  # 8KB chunks
with open('large_file.txt', 'r', encoding='utf-8') as f:
    while chunk := f.read(CHUNK_SIZE):
        process_chunk(chunk)

# BAD: Read entire file at once
with open('large_file.txt', 'r', encoding='utf-8') as f:
    content = f.read()  # May consume too much memory
```

### 2. Line-by-Line Processing

**Best Practice**: Use iteration for line-based processing.

```python
# GOOD: Line-by-line processing
with open('data.csv', 'r', encoding='utf-8') as f:
    for line in f:
        process_line(line.strip())

# BAD: Read all lines at once
with open('data.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()  # Loads entire file into memory
```

### 3. File Existence Checking

**Best Practice**: Use `try-except` rather than `exists()` checks.

```python
# GOOD: Try-except pattern
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    config = get_default_config()
except json.JSONDecodeError:
    raise ValueError('Invalid JSON configuration')

# BAD: Existence checking (race condition prone)
if Path('config.json').exists():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
else:
    config = get_default_config()
```

### 4. File Type Detection

**Best Practice**: Detect file types by content, not extension.

```python
# GOOD: Content-based detection
def detect_file_type(file_path: Path) -> str:
    with open(file_path, 'rb') as f:
        header = f.read(32)  # Read first 32 bytes
    
    if header.startswith(b'PK\x03\x04'):
        return 'zip'
    elif header.startswith(b'%PDF'):
        return 'pdf'
    elif header.startswith(b'\x89PNG'):
        return 'png'
    else:
        return 'unknown'
```

## File Writing Best Practices

### 1. Atomic Writes

**Best Practice**: Use temporary files and atomic renames for critical writes.

```python
# GOOD: Atomic write pattern
import tempfile
import shutil

def atomic_write(file_path: Path, content: str):
    temp_path = file_path.with_suffix('.tmp')
    
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        temp_path.rename(file_path)  # Atomic on most filesystems
    except Exception:
        if temp_path.exists():
            temp_path.unlink()  # Clean up
        raise
```

### 2. Directory Creation

**Best Practice**: Ensure parent directories exist.

```python
# GOOD: Automatic directory creation
output_path = Path('output/data/results.json')
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f)

# BAD: May fail if directory doesn't exist
with open('output/data/results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f)
```

### 3. File Locking

**Best Practice**: Use file locking for concurrent access.

```python
# GOOD: File locking (Unix-like systems)
import fcntl

with open('data.lock', 'w', encoding='utf-8') as f:
    fcntl.flock(f, fcntl.LOCK_EX)  # Exclusive lock
    try:
        # Critical section
        with open('data.json', 'r', encoding='utf-8') as data_file:
            data = json.load(data_file)
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)  # Release lock
```

### 4. Temporary Files

**Best Practice**: Use `tempfile` module for temporary data.

```python
# GOOD: Temporary file handling
import tempfile

with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as temp:
    temp.write('temporary data')
    temp_path = Path(temp.name)

# Process the temporary file
data = process_file(temp_path)

# Clean up
temp_path.unlink()
```

## Error Handling and Validation

### 1. Comprehensive Exception Handling

**Best Practice**: Handle specific exceptions appropriately.

```python
# GOOD: Specific exception handling
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError as e:
    logger.error(f'Configuration file not found: {e}')
    raise ConfigurationError('Missing configuration file') from e
except json.JSONDecodeError as e:
    logger.error(f'Invalid JSON in configuration: {e}')
    raise ConfigurationError('Corrupt configuration file') from e
except PermissionError as e:
    logger.error(f'Permission denied reading config: {e}')
    raise ConfigurationError('Insufficient permissions') from e
except UnicodeDecodeError as e:
    logger.error(f'Encoding error in config: {e}')
    raise ConfigurationError('Invalid file encoding') from e
```

### 2. Input Validation

**Best Practice**: Validate all inputs before file operations.

```python
# GOOD: Input validation
def safe_write_file(path: Path, content: str, encoding: str = 'utf-8'):
    # Validate path
    if not isinstance(path, Path):
        raise TypeError(f'path must be Path, got {type(path)}')
    
    # Validate content
    if not isinstance(content, str):
        raise TypeError(f'content must be str, got {type(content)}')
    
    # Validate encoding
    if encoding not in ['utf-8', 'ascii', 'latin-1']:
        raise ValueError(f'Unsupported encoding: {encoding}')
    
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file
    with open(path, 'w', encoding=encoding) as f:
        f.write(content)
```

### 3. Resource Cleanup

**Best Practice**: Ensure resources are cleaned up even on errors.

```python
# GOOD: Resource cleanup with context managers
class ManagedFile:
    def __init__(self, path: Path, mode: str = 'r'):
        self.path = path
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.path, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        return False  # Don't suppress exceptions

# Usage
with ManagedFile('data.txt', 'r') as f:
    content = f.read()
```

### 4. Retry Logic

**Best Practice**: Implement retry logic for transient errors.

```python
# GOOD: Retry logic for transient errors
import time
from functools import wraps

def retry(max_attempts: int = 3, delay: float = 0.1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            last_error = None
            
            while attempts < max_attempts:
                attempts += 1
                try:
                    return func(*args, **kwargs)
                except (IOError, OSError) as e:
                    last_error = e
                    if attempts < max_attempts:
                        time.sleep(delay * attempts)
                    continue
            
            raise last_error
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.1)
def read_with_retry(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
```

## Security Considerations

### 1. Path Traversal Protection

**Best Practice**: Prevent directory traversal attacks.

```python
# GOOD: Path traversal protection
def safe_path(base_dir: Path, user_path: str) -> Path:
    """Safely combine base directory with user-provided path."""
    if not base_dir.is_dir():
        raise ValueError(f'Base directory does not exist: {base_dir}')
    
    # Resolve to absolute path
    full_path = (base_dir / user_path).resolve()
    
    # Ensure result is within base directory
    if base_dir not in full_path.parents and full_path != base_dir:
        raise ValueError(f'Path traversal attempt: {user_path}')
    
    return full_path

# Usage
base_dir = Path('/safe/directory')
user_input = '../../etc/passwd'
try:
    safe_path = safe_path(base_dir, user_input)  # Raises ValueError
except ValueError as e:
    logger.warning(f'Path traversal prevented: {e}')
```

### 2. File Permission Management

**Best Practice**: Set appropriate file permissions.

```python
# GOOD: Permission management
import stat

def write_secure_file(path: Path, content: str):
    # Write file with restricted permissions
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Set secure permissions (owner read/write, others read-only)
    path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
```

### 3. Sensitive Data Handling

**Best Practice**: Securely handle sensitive files.

```python
# GOOD: Sensitive data handling
def handle_sensitive_file(path: Path, content: str):
    # Use secure temporary file
    with tempfile.NamedTemporaryFile(
        mode='w+', 
        encoding='utf-8',
        delete=False,
        prefix='secure_',
        suffix='.tmp'
    ) as temp:
        temp.write(content)
        temp_path = Path(temp.name)
    
    try:
        # Process sensitive data
        result = encrypt_data(temp_path)
        
        # Write to final location atomically
        final_path = Path('/secure/vault/data.enc')
        temp_path.replace(final_path)
        
        # Set restrictive permissions
        final_path.chmod(0o600)  # Owner read/write only
        
        return result
    finally:
        # Ensure cleanup
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
```

### 4. Sandboxing

**Best Practice**: Sandbox file operations when possible.

```python
# GOOD: Sandboxed file operations
import subprocess

def sandboxed_process_file(input_path: Path, output_path: Path):
    """Process file in a sandboxed environment."""
    try:
        result = subprocess.run(
            ['/usr/bin/sandboxed_processor', str(input_path), str(output_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise RuntimeError(f'Processing failed: {result.stderr}')
        
        return output_path
    except subprocess.TimeoutExpired:
        raise RuntimeError('File processing timed out')
```

## Performance Optimization

### 1. Buffered I/O

**Best Practice**: Use appropriate buffer sizes.

```python
# GOOD: Buffered I/O
BUFFER_SIZE = 65536  # 64KB buffer

def copy_file(src: Path, dst: Path):
    with open(src, 'rb') as src_file:
        with open(dst, 'wb') as dst_file:
            while chunk := src_file.read(BUFFER_SIZE):
                dst_file.write(chunk)
```

### 2. Memory-Mapped Files

**Best Practice**: Use memory mapping for large files.

```python
# GOOD: Memory-mapped files
import mmap

def process_large_file(file_path: Path):
    with open(file_path, 'r+b') as f:
        # Map the file into memory
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            # Process file in memory
            data = mm.read(1024)
            # ... process data
```

### 3. Parallel Processing

**Best Practice**: Parallelize file operations where possible.

```python
# GOOD: Parallel file processing
from concurrent.futures import ThreadPoolExecutor

def process_files_parallel(file_paths: List[Path]):
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_single_file, file_paths))
    return results
```

### 4. Lazy Loading

**Best Practice**: Load data on-demand.

```python
# GOOD: Lazy file loading
class LazyFileLoader:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._content = None
    
    @property
    def content(self):
        if self._content is None:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self._content = f.read()
        return self._content

# Usage
loader = LazyFileLoader(Path('large_file.txt'))
# Content is only loaded when accessed
print(loader.content)
```

## Testing Strategies

### 1. Mocking File Operations

**Best Practice**: Use `unittest.mock` for file operation testing.

```python
# GOOD: Mocking file operations
from unittest.mock import patch, mock_open
import json

def test_config_loading():
    mock_data = {'setting': 'value'}
    
    with patch('builtins.open', mock_open(read_data=json.dumps(mock_data))):
        config = load_config('dummy.json')
        
        assert config == mock_data
```

### 2. Temporary Test Files

**Best Practice**: Use temporary files in tests.

```python
# GOOD: Temporary test files
import pytest

@pytest.fixture
def temp_config_file(tmp_path):
    config = {'test': 'value'}
    config_file = tmp_path / 'config.json'
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f)
    
    return config_file

def test_with_temp_file(temp_config_file):
    config = load_config(temp_config_file)
    assert config['test'] == 'value'
```

### 3. Test Coverage for Edge Cases

**Best Practice**: Test edge cases and error conditions.

```python
# GOOD: Edge case testing
import pytest

def test_file_operations_edge_cases():
    # Test missing file
    with pytest.raises(FileNotFoundError):
        load_config(Path('nonexistent.json'))
    
    # Test invalid JSON
    with pytest.raises(json.JSONDecodeError):
        load_config(Path('invalid.json'))
    
    # Test permission error
    with pytest.raises(PermissionError):
        # Simulate permission error
        pass
```

### 4. Integration Testing

**Best Practice**: Test complete file operation workflows.

```python
# GOOD: Integration testing
def test_file_processing_workflow(tmp_path):
    # Setup
    input_file = tmp_path / 'input.txt'
    output_file = tmp_path / 'output.txt'
    
    input_file.write_text('test data', encoding='utf-8')
    
    # Execute
    process_file(input_file, output_file)
    
    # Verify
    assert output_file.exists()
    assert output_file.read_text(encoding='utf-8') == 'processed data'
```

## Logging and Monitoring

### 1. Comprehensive Logging

**Best Practice**: Log all file operations with context.

```python
# GOOD: Comprehensive logging
import logging

logger = logging.getLogger(__name__)

def log_file_operation(operation: str, path: Path, **kwargs):
    context = {
        'operation': operation,
        'path': str(path),
        'size': path.stat().st_size if path.exists() else 0,
        **kwargs
    }
    
    logger.info('File operation', extra=context)

def read_file_with_logging(path: Path):
    log_file_operation('read', path)
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        log_file_operation('read_success', path, bytes_read=len(content))
        return content
    except Exception as e:
        log_file_operation('read_error', path, error=str(e))
        raise
```

### 2. Performance Monitoring

**Best Practice**: Monitor file operation performance.

```python
# GOOD: Performance monitoring
import time

def timed_file_operation(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            
            # Log performance metrics
            logger.info(f'{func.__name__} completed in {elapsed:.4f}s')
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.error(f'{func.__name__} failed after {elapsed:.4f}s: {e}')
            raise
    
    return wrapper

@timed_file_operation
def read_large_file(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
```

### 3. Operation Tracking

**Best Practice**: Track file operations for auditing.

```python
# GOOD: Operation tracking
class FileOperationTracker:
    def __init__(self):
        self.operations = []
    
    def track(self, operation: str, path: Path, success: bool, **metadata):
        self.operations.append({
            'timestamp': time.time(),
            'operation': operation,
            'path': str(path),
            'success': success,
            **metadata
        })
    
    def get_stats(self):
        return {
            'total': len(self.operations),
            'success': sum(1 for op in self.operations if op['success']),
            'failure': sum(1 for op in self.operations if not op['success'])
        }

# Usage
tracker = FileOperationTracker()

try:
    content = read_file('data.txt')
    tracker.track('read', Path('data.txt'), True, bytes_read=len(content))
except Exception as e:
    tracker.track('read', Path('data.txt'), False, error=str(e))
```

## File Format Specifics

### 1. JSON Files

**Best Practice**: Use `json` module with proper error handling.

```python
# GOOD: JSON file handling
def read_json_file(path: Path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON in {path}: {e}')
        raise ValueError(f'Corrupt JSON file: {path}') from e
    except FileNotFoundError:
        logger.error(f'JSON file not found: {path}')
        raise

def write_json_file(path: Path, data, indent: int = 2):
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except TypeError as e:
        logger.error(f'Non-serializable data for {path}: {e}')
        raise ValueError(f'Data contains non-serializable types') from e
```

### 2. CSV Files

**Best Practice**: Use `csv` module for structured data.

```python
# GOOD: CSV file handling
import csv

def read_csv_file(path: Path):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))

def write_csv_file(path: Path, data: List[Dict], fieldnames: List[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
```

### 3. Binary Files

**Best Practice**: Use binary mode for non-text data.

```python
# GOOD: Binary file handling
def read_binary_file(path: Path, chunk_size: int = 8192) -> bytes:
    with open(path, 'rb') as f:
        return f.read()

def write_binary_file(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'wb') as f:
        f.write(data)
```

### 4. TOML Files

**Best Practice**: Use `tomllib` (Python 3.11+) for TOML.

```python
# GOOD: TOML file handling
import tomllib

def read_toml_file(path: Path):
    try:
        with open(path, 'rb') as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        logger.error(f'Invalid TOML in {path}: {e}')
        raise ValueError(f'Corrupt TOML file: {path}') from e

def write_toml_file(path: Path, data: dict):
    try:
        import tomli_w
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'wb') as f:
            tomli_w.dump(data, f)
    except ImportError:
        # Fallback to JSON
        logger.warning('tomli_w not available, using JSON fallback')
        write_json_file(path, data)
```

## Advanced Patterns

### 1. File Observer Pattern

**Best Practice**: Monitor file changes for reactive processing.

```python
# GOOD: File observer pattern
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.json'):
            self.callback(Path(event.src_path))

def watch_config_file(config_path: Path, callback):
    event_handler = ConfigFileHandler(callback)
    observer = Observer()
    observer.schedule(event_handler, str(config_path.parent), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

### 2. File Factory Pattern

**Best Practice**: Use factory pattern for file type detection.

```python
# GOOD: File factory pattern
class FileReaderFactory:
    @staticmethod
    def get_reader(file_path: Path):
        if file_path.suffix == '.json':
            return JSONFileReader()
        elif file_path.suffix == '.csv':
            return CSVFileReader()
        elif file_path.suffix == '.toml':
            return TOMLFileReader()
        else:
            return TextFileReader()

# Usage
reader = FileReaderFactory.get_reader(Path('data.json'))
data = reader.read(Path('data.json'))
```

### 3. File Strategy Pattern

**Best Practice**: Use strategy pattern for different file operations.

```python
# GOOD: File strategy pattern
from abc import ABC, abstractmethod

class FileStrategy(ABC):
    @abstractmethod
    def process(self, file_path: Path):
        pass

class JSONProcessingStrategy(FileStrategy):
    def process(self, file_path: Path):
        data = read_json_file(file_path)
        return process_json_data(data)

class CSVProcessingStrategy(FileStrategy):
    def process(self, file_path: Path):
        data = read_csv_file(file_path)
        return process_csv_data(data)

def process_file(file_path: Path, strategy: FileStrategy):
    return strategy.process(file_path)
```

### 4. File Decorator Pattern

**Best Practice**: Add functionality to file operations dynamically.

```python
# GOOD: File decorator pattern
class FileOperationDecorator:
    def __init__(self, file_operation):
        self._file_operation = file_operation
    
    def __call__(self, *args, **kwargs):
        # Pre-processing
        self.before_operation(*args, **kwargs)
        
        # Execute operation
        result = self._file_operation(*args, **kwargs)
        
        # Post-processing
        self.after_operation(*args, **kwargs)
        
        return result
    
    def before_operation(self, *args, **kwargs):
        pass
    
    def after_operation(self, *args, **kwargs):
        pass

class LoggingFileDecorator(FileOperationDecorator):
    def before_operation(self, path, *args, **kwargs):
        logger.info(f'Starting file operation on {path}')
    
    def after_operation(self, path, *args, **kwargs):
        logger.info(f'Completed file operation on {path}')

# Usage
@LoggingFileDecorator
def read_file(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
```

## Synth-GPR Specific Recommendations

### 1. Data Access Layer Integration

**Best Practice**: Route all file operations through `src/data_access/`.

```python
# GOOD: Using data access layer
from src.data_access import FileReader, FileWriter, TOMLReader, TOMLWriter

# Read files
reader = FileReader()
config = reader.read('config.toml')  # Auto-detects TOML

# Write files  
writer = FileWriter()
writer.write('output.json', data)

# Specialized readers
toml_reader = TOMLReader()
scene_config = toml_reader.read('scene.toml')

# Specialized writers
toml_writer = TOMLWriter()
toml_writer.write('results.toml', results)
```

### 2. Repository Pattern Usage

**Best Practice**: Use repository pattern for data persistence.

```python
# GOOD: Repository pattern usage
from src.repositories import SceneRepository

# Create repository
repo = SceneRepository()

# Store scene
scene_id = repo.store_scene(scene_model)

# Retrieve scene
scene = repo.get_scene(scene_id)

# List all scenes
all_scenes = repo.list_scenes()
```

### 3. TOML Best Practices

**Best Practice**: Follow TOML conventions for configuration.

```toml
# GOOD: Well-structured TOML
[sim]
freq_hz = 400e6
domain_x = 1.0
antenna_clearance = 0.5
air_buffer = 0.1

[source]
tx_x = 0.5
tx_y = 0.9
tx_z = 0.05
waveform = "ricker"

[lab]
title = "Clean ballast reference"
date = "2026-07-08"
notes = "Generated for calibration"

[[layer]]
name = "ballast"
thickness = 0.3
packed = true
rock_radius_min = 0.02
rock_radius_max = 0.05

[[layer]]
name = "subgrade"
thickness = 0.2
eps = 9.0
sigma = 0.01
```

### 4. Error Handling in Synth-GPR

**Best Practice**: Use consistent error handling patterns.

```python
# GOOD: Synth-GPR error handling
def read_scene_config(path: Path):
    try:
        reader = TOMLReader()
        config = reader.read(path)
        
        # Validate required fields
        if 'sim' not in config:
            raise ValueError('Missing [sim] section in configuration')
        
        return config
        
    except FileNotFoundError as e:
        logger.error(f'Scene configuration not found: {path}')
        raise SceneConfigurationError(f'Missing scene file: {path}') from e
    except tomllib.TOMLDecodeError as e:
        logger.error(f'Invalid TOML in scene configuration: {path}')
        raise SceneConfigurationError(f'Corrupt scene file: {path}') from e
    except ValueError as e:
        logger.error(f'Invalid scene configuration: {path} - {e}')
        raise SceneConfigurationError(f'Invalid configuration: {e}') from e
```

### 5. Testing File Operations

**Best Practice**: Comprehensive testing for file operations.

```python
# GOOD: Synth-GPR file operation testing
def test_scene_loading(tmp_path):
    # Create test scene file
    scene_content = """
    [sim]
    freq_hz = 400e6
    
    [[layer]]
    name = "test"
    thickness = 0.1
    """
    
    scene_file = tmp_path / 'test.toml'
    scene_file.write_text(scene_content)
    
    # Test loading
    from src.scene_model import parse_toml
    scene = parse_toml(scene_file)
    
    assert scene.freq_hz == 400e6
    assert len(scene.layers) == 1
    assert scene.layers[0].name == 'test'
```

### 6. Performance Optimization for GPR Data

**Best Practice**: Optimize for large GPR datasets.

```python
# GOOD: GPR data optimization
def process_large_dzt_file(dzt_path: Path, chunk_size: int = 1024):
    """Process DZT file in chunks to avoid memory issues."""
    from src.dzt_io import read_dzt_traces
    
    # Process in chunks
    for chunk_start in range(0, get_total_traces(dzt_path), chunk_size):
        chunk_end = min(chunk_start + chunk_size, get_total_traces(dzt_path))
        
        traces, meta = read_dzt_traces(
            dzt_path, 
            start_trace=chunk_start,
            num_traces=chunk_end - chunk_start
        )
        
        # Process chunk
        process_trace_chunk(traces, meta)
        
        # Clean up
        del traces
```

### 7. Atomic Operations for Critical Files

**Best Practice**: Use atomic operations for important configuration files.

```python
# GOOD: Atomic configuration updates
def update_configuration(config_path: Path, updates: dict):
    """Atomically update configuration file."""
    temp_path = config_path.with_suffix('.tmp')
    
    try:
        # Read current config
        reader = TOMLReader()
        config = reader.read(config_path)
        
        # Apply updates
        config.update(updates)
        
        # Write to temp file
        writer = TOMLWriter()
        writer.write(temp_path, config)
        
        # Atomic replace
        temp_path.replace(config_path)
        
    except Exception:
        # Clean up temp file on error
        if temp_path.exists():
            temp_path.unlink()
        raise
```

## Summary

This comprehensive guide covers best practices for file handling in Python applications, with specific recommendations for the Synth-GPR codebase. Key takeaways:

### General Principles
1. **Use context managers** for all file operations
2. **Prefer pathlib** over os.path
3. **Specify encoding explicitly** (typically 'utf-8')
4. **Choose correct file modes** (text vs binary)

### Advanced Patterns
1. **Atomic writes** for critical operations
2. **Proper error handling** with specific exceptions
3. **Path validation** to prevent traversal attacks
4. **Performance optimization** for large files

### Synth-GPR Specific
1. **Use data access layer** for consistency
2. **Follow TOML conventions** for configuration
3. **Implement repository pattern** for data persistence
4. **Optimize for GPR data** size and format

### Testing and Monitoring
1. **Mock file operations** in unit tests
2. **Use temporary files** for test isolation
3. **Comprehensive logging** for debugging
4. **Performance monitoring** for optimization

By following these best practices, the Synth-GPR codebase can achieve robust, maintainable, and secure file handling that supports both research and production use cases.