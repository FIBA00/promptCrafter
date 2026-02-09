"""
================================================================================
Log Manager (`log_man.py`)
================================================================================
Version: 1.0
Author: [FRAOL BULTI]
Date: [2025]
================================================================================

OVERVIEW:
---------
This module provides a centralized, thread-safe logging system for the entire
application. It is designed to be simple to use while offering robust features
like per-script log files, automatic log cleanup and backup, and standardized
formatting. The primary goal is to ensure consistent and reliable logging
across all components with minimal setup.

ARCHITECTURE:
-------------
1.  **Singleton Logger per Script**: The `get_logger(script_path)` function acts
    as the main entry point. It provides a unique, singleton `logging.Logger`
    instance for each calling script, preventing duplicate log handlers and
    ensuring consistent output.

2.  **Thread-Safe Initialization**: A global lock (`_logger_lock`) ensures that
    logger instances and the initial log directory cleanup are handled in a
    thread-safe manner, preventing race conditions in multi-threaded environments.

3.  **Automatic Log Cleanup and Backup**: On the first call to `get_logger` in a
    process, the module automatically backs up existing log files to a
    timestamped folder and then cleans the main log directory. This ensures each
    application run starts with fresh log files.

4.  **Dual Handlers**: Each logger is pre-configured with two handlers:
    -   A `StreamHandler` to output logs to the console (stdout) for real-time
        monitoring.
    -   A `FileHandler` to write logs to a dedicated file (`<script_name>.log`)
        for persistent storage and post-run analysis.

5.  **Custom Logger with Automatic Tracebacks**: It uses a custom `TracebackLogger`
    class that automatically includes full stack traces for `error()` and
    `critical()` level messages, simplifying debugging without needing to
    manually set `exc_info=True`.

6.  **Dependency on `app_storage_man`**: The module relies on `app_storage_man`
    to provide standardized paths for log and backup directories, ensuring
    consistency across the application.

MAINTENANCE & USAGE:
--------------------
-   **Usage**: To get a logger in any module, simply import `get_logger` and call
    it with `__file__`:
    `from utils.log_man import get_logger`
    `lg = get_logger(__file__)`

-   **Configuration**: Log levels are currently hardcoded to `DEBUG`. To make them
    configurable (e.g., based on an environment variable or a config file),
    modify the `setLevel()` calls within the `LogManager` class.

-   **Log Format**: The log message format is defined in `LogManager.__init__`.
    This is the central place to adjust the format for all loggers.

-   **Backup and Cleanup Logic**: The backup strategy is a simple daily-timestamped
    copy. If more advanced log rotation (e.g., by size, or keeping N backups) is
    required, the `backup_logs_dir` and `clean_logs_dir` functions should be
    updated.

-   **Dependencies**: This module's functionality is critically dependent on
    `app_storage_man.py` providing valid paths. If logging fails, first ensure
    that the paths defined in `app_storage_man` are correct and accessible.

"""

# utils/t1_log_manager.py [utilities tool / tool 1 lgmanager]
# here we manage our logging system, with a single instance of the lgand a single instance of the handler
# also log files are managed[create, check, delete, etc]
import os
import sys


import logging
from logging import (
    getLogger,
    StreamHandler,
    FileHandler,
    Formatter,
    INFO,
)
from threading import Lock
from typing import Dict

""" 
Global lock for thread safety in logger creation, Import centralized app storage,
Ensures only one thread creates a lgat a time, Dictionary to hold lginstances per script, 
Default log directory for all log files, Global flag to ensure logs directory is cleaned only once per process
"""


LOG_DIR: str = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
)
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
_logger_lock: Lock = Lock()
_logger_instances: Dict[str, "LogManager"] = {}
_logs_dir_cleaned: bool = False


class TracebackLogger(logging.Logger):
    def error(self, msg, *args, **kwargs):
        if sys.exc_info()[0] is not None and "exc_info" not in kwargs:
            kwargs["exc_info"] = True
        super().error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if sys.exc_info()[0] is not None and "exc_info" not in kwargs:
            kwargs["exc_info"] = True
        super().critical(msg, *args, **kwargs)


# Register the custom lgclass globally
logging.setLoggerClass(TracebackLogger)


class LogManager:
    """
    LogManager manages a single lginstance per script, with both console and file handlers.
    It also manages log file creation, cleanup, and formatting.

    Attributes:
        log_file (str): Path to the log file for the script.
        lg(logging.Logger): Logger instance for the script.
    """

    def __init__(self, script_name: str) -> None:
        """
        Initialize the LogManager for a given script.

        Args:
            script_name (str): The name for the logger.

        Side Effects:
            - Ensures the log directory exists.
            - Sets up a lgwith both console and file handlers.
        """
        # Extract script name for log file naming
        # script_name: str = os.path.splitext(os.path.basename(script_path))[
        #     0
        # ]  # e.g., "my_script"

        # Log directory is guaranteed to exist via app storage
        # No need to create it manually

        # Construct the log file path for this script
        self.log_file: str = os.path.join(LOG_DIR, f"{script_name}.log")
        # Create or retrieve a lgwith the script name
        self.logger = getLogger(script_name)
        self.logger.setLevel(INFO)  # Set default log level to INFO for all handlers
        self.logger.propagate = False  # Prevent logging to root logger (double logging)
        # Prevent duplicate handlers if lgalready exists
        if not self.logger.handlers:
            # Create a console (stream) handler for real-time output
            stream_handler: StreamHandler = StreamHandler(sys.stdout)
            stream_handler.setLevel(INFO)
            # Create a file handler for persistent log storage
            file_handler: FileHandler = FileHandler(self.log_file, encoding="utf-8")
            file_handler.setLevel(INFO)
            # Define a formatter for consistent log message formatting
            # Formatter includes date and time (no microseconds), logger name, level, line number, and message
            # Use datefmt for formatting the date and time in log messages.
            # The datefmt argument specifies the format for %(asctime)s in the log output.
            log_format = (
                "%(asctime)s - %(name)s - %(levelname)s - [%(lineno)d] - %(message)s"
            )
            date_format = "%Y-%m-%d %H:%M:%S"
            formatter: Formatter = Formatter(fmt=log_format, datefmt=date_format)
            # Attach the formatter to both handlers
            stream_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            # Add both handlers to the logger
            self.logger.addHandler(stream_handler)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        """
        Return the lginstance managed by this LogManager.

        Returns:
            logging.Logger: The lginstance for the script.
        """
        return self.logger


# Module-level function for easy lgretrieval
# Usage: from utils.sys_log_manager import get_logger; lg= get_logger(__file__)
def get_logger(script_path: str):
    """
    Retrieve a singleton logger for the given script path.
    Ensures only one logger per script, with file and console handlers.

    Args:
        script_path (str): The path to the script requesting a lg

    Returns:
        logging.Logger: The lginstance for the script.
    """
    # global _logs_dir_cleaned
    with _logger_lock:
        # Clean logs directory only once per process, before any lgis created

        # # Backup logs before cleaning
        # backup_logs_dir(log_dir, str(paths.bkp))

        # if not _logs_dir_cleaned:
        #     clean_logs_dir(LOG_DIR)
        #     _logs_dir_cleaned = True
        # Extract script name for singleton lgmapping
        if os.path.sep in script_path or (
            os.path.altsep and os.path.altsep in script_path
        ):
            script_name: str = os.path.splitext(os.path.basename(script_path))[0]
        else:
            script_name: str = script_path

        # If lgdoes not exist for this script, create and store it
        if script_name not in _logger_instances:
            _logger_instances[script_name] = LogManager(script_name)
        # Return the lginstance for this script
        return _logger_instances[script_name].get_logger()


# lg = get_logger(__file__)
# lg.info("this is test message")
# lg.debug("this is test message")
# lg.error("this is test message")
# lg.warning("this is test message")
# lg.critical("this is test message")
