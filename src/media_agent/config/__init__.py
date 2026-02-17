"""Configuration module."""

from .settings import Settings, get_settings, get_project_root, get_config_dir, get_db_path
from .loader import load_product_config, list_available_products, get_faqs_from_config
from .logging_config import setup_logging, get_logger, init_default_logging
from .errors import MediaAgentError, handle_error, ErrorCode

__all__ = [
    "Settings",
    "get_settings",
    "get_project_root",
    "get_config_dir",
    "get_db_path",
    "load_product_config",
    "list_available_products",
    "get_faqs_from_config",
    "setup_logging",
    "get_logger",
    "init_default_logging",
    "MediaAgentError",
    "handle_error",
    "ErrorCode",
]
