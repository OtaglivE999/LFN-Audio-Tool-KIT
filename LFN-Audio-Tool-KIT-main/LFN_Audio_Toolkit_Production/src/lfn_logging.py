"""
LFN Audio Toolkit - Centralized Logging Configuration
======================================================

Provides consistent logging across all toolkit modules with configurable
verbosity levels, file output, and structured formatting.

Usage:
    from lfn_logging import get_logger
    
    logger = get_logger(__name__)
    logger.info("Processing audio file")
    logger.debug("Detailed diagnostic information")
    logger.warning("Non-critical issue detected")
    logger.error("Operation failed")
"""
# -*- coding: utf-8 -*-
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler


# Default configuration
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_DIR = "logs"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep 5 backup log files

# Console color codes for different log levels
COLORS = {
    'DEBUG': '\033[36m',      # Cyan
    'INFO': '\033[32m',       # Green
    'WARNING': '\033[33m',    # Yellow
    'ERROR': '\033[31m',      # Red
    'CRITICAL': '\033[35m',   # Magenta
    'RESET': '\033[0m'
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to console output"""
    
    def format(self, record):
        if sys.platform != 'win32' or os.environ.get('COLORTERM'):
            # Add color for terminals that support it
            levelname = record.levelname
            if levelname in COLORS:
                record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
        return super().format(record)


def get_log_level_from_env():
    """Get log level from environment variable"""
    level_name = os.environ.get('LFN_LOG_LEVEL', '').upper()
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return level_map.get(level_name, DEFAULT_LOG_LEVEL)


def setup_logging(
    module_name,
    log_to_file=None,
    log_to_console=True,
    log_level=None,
    log_dir=None
):
    """
    Set up logging configuration for a module
    
    Args:
        module_name: Name of the module (usually __name__)
        log_to_file: If True or filename string, enable file logging
        log_to_console: If True, enable console logging
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (default: 'logs/')
    
    Returns:
        Configured logger instance
    """
    # Determine log level
    if log_level is None:
        log_level = get_log_level_from_env()
    
    # Get or create logger
    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Determine log directory
    if log_dir is None:
        # Check environment variable first
        env_log_dir = os.environ.get('LFN_LOG_DIR')
        if env_log_dir:
            log_dir = Path(env_log_dir)
        else:
            # Try to find project root (more robust than assuming parent.parent)
            current = Path(__file__).resolve().parent
            # Look for project markers
            for _ in range(3):
                if (current / 'preflight_check.py').exists() or (current / 'setup.py').exists():
                    log_dir = current / DEFAULT_LOG_DIR
                    break
                current = current.parent
            else:
                # Fallback to parent directory
                log_dir = Path(__file__).parent.parent / DEFAULT_LOG_DIR
    else:
        log_dir = Path(log_dir)
    
    # Create log directory if needed
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Define formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = ColoredFormatter(
        fmt='[%(levelname)s] %(name)s - %(message)s'
    )
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler(s)
    if log_to_file:
        # Determine filename
        if isinstance(log_to_file, str):
            log_filename = log_to_file
        else:
            # Auto-generate filename
            safe_module = module_name.replace('.', '_')
            log_filename = f"lfn_{safe_module}.log"
        
        log_path = log_dir / log_filename
        
        # Rotating file handler (prevents log files from growing indefinitely)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        # Also create an error-only log file
        error_log_path = log_dir / log_filename.replace('.log', '_error.log')
        error_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
    
    # Check for debug mode from environment
    if os.environ.get('LFN_DEBUG') == '1':
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
    
    return logger


def get_logger(module_name, **kwargs):
    """
    Convenience function to get a configured logger
    
    Args:
        module_name: Name of the module (usually __name__)
        **kwargs: Additional arguments passed to setup_logging()
    
    Returns:
        Configured logger instance
    
    Example:
        logger = get_logger(__name__)
        logger.info("Processing started")
    """
    # Check environment for file logging preference
    env_log_file = os.environ.get('LFN_LOG_FILE')
    if env_log_file and 'log_to_file' not in kwargs:
        kwargs['log_to_file'] = env_log_file
    elif 'log_to_file' not in kwargs:
        # Enable file logging by default for main modules
        if any(name in module_name for name in ['batch', 'realtime', 'recorder', 'health']):
            kwargs['log_to_file'] = True
    
    return setup_logging(module_name, **kwargs)


def log_system_info(logger):
    """
    Log system information for debugging purposes
    
    Args:
        logger: Logger instance to use
    """
    import platform
    
    logger.debug("="*60)
    logger.debug("System Information")
    logger.debug("="*60)
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Platform: {platform.platform()}")
    logger.debug(f"Processor: {platform.processor()}")
    
    try:
        import psutil
        logger.debug(f"CPU cores: {psutil.cpu_count(logical=False)} physical, "
                     f"{psutil.cpu_count(logical=True)} logical")
        
        memory = psutil.virtual_memory()
        logger.debug(f"RAM: {memory.total / (1024**3):.2f} GB total, "
                     f"{memory.available / (1024**3):.2f} GB available")
        
        disk = psutil.disk_usage('.')
        logger.debug(f"Disk: {disk.total / (1024**3):.2f} GB total, "
                     f"{disk.free / (1024**3):.2f} GB free")
    except ImportError:
        logger.debug("psutil not available - skipping detailed system metrics")
    
    logger.debug("="*60)


def log_exception(logger, exception, message="Exception occurred"):
    """
    Log an exception with full traceback
    
    Args:
        logger: Logger instance
        exception: Exception object
        message: Custom message to include
    """
    import traceback
    
    logger.error(f"{message}: {type(exception).__name__}: {str(exception)}")
    logger.debug("Full traceback:")
    for line in traceback.format_tb(exception.__traceback__):
        logger.debug(line.rstrip())


def log_function_call(logger, level=logging.DEBUG):
    """
    Decorator to log function calls with arguments
    
    Args:
        logger: Logger instance
        level: Logging level for the message
    
    Example:
        @log_function_call(logger)
        def my_function(arg1, arg2):
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            
            logger.log(level, f"Calling {func.__name__}({signature})")
            
            try:
                result = func(*args, **kwargs)
                logger.log(level, f"{func.__name__} returned {result!r}")
                return result
            except Exception as e:
                logger.exception(f"{func.__name__} raised {type(e).__name__}: {e}")
                raise
        
        return wrapper
    return decorator


def create_session_log(session_name, log_dir=None):
    """
    Create a session-specific log file
    
    Args:
        session_name: Name for this session (e.g., 'batch_analysis')
        log_dir: Directory for log files
    
    Returns:
        Path to created log file
    """
    if log_dir is None:
        script_dir = Path(__file__).parent.parent
        log_dir = script_dir / DEFAULT_LOG_DIR
    else:
        log_dir = Path(log_dir)
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"{session_name}_{timestamp}.log"
    log_path = log_dir / log_filename
    
    return log_path


# Example usage demonstration
if __name__ == "__main__":
    # Example 1: Basic logger
    logger = get_logger(__name__)
    logger.info("This is an info message")
    logger.debug("This is a debug message (may not show by default)")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Example 2: Logger with file output
    logger2 = get_logger("example_module", log_to_file=True)
    logger2.info("This will be logged to file and console")
    
    # Example 3: System info logging
    log_system_info(logger)
    
    # Example 4: Exception logging
    try:
        raise ValueError("Example exception")
    except Exception as e:
        log_exception(logger, e, "Demonstrating exception logging")
    
    print("\nCheck the 'logs/' directory for log files!")
