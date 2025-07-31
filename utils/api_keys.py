"""API key management for Astra bot"""

import os
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("Astra")

# API key settings
API_KEYS = {
    "nasa": {
        "key": os.getenv("NASA_API_KEY", "DEMO_KEY"),
        "rate_limit": {
            "hourly": (
                30 if os.getenv("NASA_API_KEY") else 10
            ),  # DEMO_KEY has lower limits
            "daily": 1000 if os.getenv("NASA_API_KEY") else 50,
        },
        "base_url": "https://api.nasa.gov",
    }
}


def get_api_key(service: str) -> Optional[str]:
    """Get API key for a specific service"""
    if service in API_KEYS:
        return API_KEYS[service]["key"]
    return None


def get_service_url(service: str) -> Optional[str]:
    """Get base URL for a specific service"""
    if service in API_KEYS:
        return API_KEYS[service]["base_url"]
    return None
