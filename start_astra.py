#!/usr/bin/env python3
"""
Astra Bot Startup Script
Ensures proper environment configuration before starting the bot
"""

import os
import sys

def setup_environment():
    """Setup environment variables to suppress warnings and optimize performance"""
    
    # Google Cloud / gRPC Configuration - MUST be set before any imports
    os.environ["GRPC_VERBOSITY"] = "ERROR"
    os.environ["GLOG_minloglevel"] = "2"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS_DISABLED"] = "true"
    
    # TensorFlow/ABSL logging suppression
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    os.environ["ABSL_LOGGING_VERBOSITY"] = "1"
    
    # gRPC optimizations
    os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "0"
    os.environ["GRPC_POLL_STRATEGY"] = "poll"
    
    # Python optimizations
    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    
    # Discord.py optimizations
    os.environ["PYTHONASYNCIODEBUG"] = "0"
    
    print("✅ Environment configured for optimal bot operation")

def main():
    """Main startup function"""
    print("🚀 Starting Astra Bot with optimized environment...")
    
    # Configure environment FIRST
    setup_environment()
    
    # Now import and run the main bot
    try:
        # Import the main bot module
        import importlib.util
        spec = importlib.util.spec_from_file_location("bot", "bot.1.0.py")
        bot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot_module)
        
        # Run the bot's main function if it exists
        if hasattr(bot_module, 'main'):
            import asyncio
            asyncio.run(bot_module.main())
        else:
            print("❌ No main function found in bot module")
            
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()