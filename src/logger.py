import logging
import sys
import warnings

try:
    from langchain_core._api.deprecation import LangChainDeprecationWarning

    warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
except ImportError:
    warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    from colorlog import ColoredFormatter

    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False


def setup_logger(name: str, level=logging.INFO, use_color: bool = True):
    """
    Set up a logger with console handler for CloudWatch and colored terminal output

    Args:
        name: Logger name (usually __name__ of the module)
        level: Logging level
        use_color: Whether to use colored output (requires colorlog package)

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create formatter
    if use_color and COLORLOG_AVAILABLE:
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Console handler (CloudWatch captures stdout/stderr)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
