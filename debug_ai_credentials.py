#!/usr/bin/env python3
"""
Quick Railway AI Debug Script
Add this to your bot startup to see what's happening with AI credentials
"""

import os
import logging

def debug_ai_credentials():
    """Debug AI credentials on Railway"""
    logger = logging.getLogger("astra.ai_debug")
    
    logger.info("🔍 AI CREDENTIALS DEBUG")
    logger.info("=" * 40)
    
    # Check environment variables directly
    ai_key = os.getenv('AI_API_KEY')
    ai_base_url = os.getenv('AI_BASE_URL')
    ai_model = os.getenv('AI_MODEL')
    ai_provider = os.getenv('AI_PROVIDER')
    
    logger.info(f"Direct env check:")
    logger.info(f"  AI_API_KEY: {'SET' if ai_key else 'NOT SET'} ({'*' * 10 + ai_key[-10:] if ai_key else 'None'})")
    logger.info(f"  AI_BASE_URL: {ai_base_url or 'NOT SET'}")
    logger.info(f"  AI_MODEL: {ai_model or 'NOT SET'}")
    logger.info(f"  AI_PROVIDER: {ai_provider or 'NOT SET'}")
    
    # Try importing Railway config
    try:
        from config.railway_config import get_railway_config
        
        config = get_railway_config()
        universal_config = config.get_universal_ai_config()
        
        logger.info(f"Railway config check:")
        logger.info(f"  API Key: {'SET' if universal_config.get('api_key') else 'NOT SET'}")
        logger.info(f"  Base URL: {universal_config.get('base_url', 'NOT SET')}")
        logger.info(f"  Model: {universal_config.get('model', 'NOT SET')}")
        
        if not universal_config.get('api_key'):
            logger.error("🚨 CRITICAL: No API key found in Railway config!")
            logger.error("🔧 FIX: Set AI_API_KEY environment variable on Railway")
        
    except Exception as e:
        logger.error(f"Railway config error: {e}")
    
    # Try Universal AI Client
    try:
        from ai.universal_ai_client import UniversalAIClient
        
        client = UniversalAIClient()
        logger.info(f"UniversalAIClient check:")
        logger.info(f"  Available: {client.is_available()}")
        logger.info(f"  API Key: {'SET' if client.api_key else 'NOT SET'}")
        logger.info(f"  Base URL: {client.base_url}")
        logger.info(f"  Model: {client.model}")
        
        if not client.api_key:
            logger.error("🚨 CRITICAL: UniversalAIClient has no API key!")
        
    except Exception as e:
        logger.error(f"UniversalAIClient error: {e}")
    
    logger.info("=" * 40)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    debug_ai_credentials()
