"""
Utility modules for Astra Bot
Provides database, error handling, permissions, and HTTP utilities
"""

# Import all utility modules to ensure they're available
from utils.database import db, SimpleDatabaseManager as DatabaseManager
from utils.enhanced_error_handler import ErrorHandler
from utils.permissions import (
    PermissionLevel,
    PermissionManager,
    has_permission,
    setup_permissions,
)
from utils.http_manager import (
    HTTPClient,
    get_session,
    get_json,
    post_json,
    cleanup_http,
)

__all__ = [
    "db",
    "DatabaseManager",
    "ErrorHandler",
    "ErrorSeverity",
    "setup_error_handler",
    "PermissionLevel",
    "PermissionManager",
    "has_permission",
    "setup_permissions",
    "HTTPClient",
    "get_session",
    "get_json",
    "post_json",
    "cleanup_http",
]
