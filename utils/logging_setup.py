"""
Logging configuration for SANDI system.
"""

import logging
import warnings


def setup_logging():
    """Configure logging and suppress warnings."""

    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Suppress various warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)

    return logging.getLogger("sandi")


logger = setup_logging()
