#!/usr/bin/env python3
"""
Environment Configuration Script
Configures environment variables to suppress warnings and optimize performance
"""

import os
import sys

def configure_environment():
    """Configure environment variables for optimal Discord bot operation"""
    
    print("🔧 Configuring Environment Variables...")
    
    # Google Cloud / GRPC Configuration
    # Suppress ALTS credentials warnings
    os.environ['GRPC_VERBOSITY'] = 'ERROR'
    os.environ['GLOG_minloglevel'] = '2'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS_DISABLED'] = 'true'
    
    # Discord.py optimizations
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # Logging configuration
    os.environ['ASTRA_LOG_LEVEL'] = 'INFO'
    
    print("✅ Environment configured:")
    print("  • GRPC verbosity set to ERROR (suppresses ALTS warnings)")
    print("  • Google logging minimized")
    print("  • Python unbuffered output enabled")
    print("  • Astra logging level set to INFO")
    
    return True

def create_env_file():
    """Create a .env file with optimal settings"""
    
    env_content = """# Astra Bot Environment Configuration
# Generated automatically - suppress warnings and optimize performance

# Google Cloud / GRPC Settings
GRPC_VERBOSITY=ERROR
GLOG_minloglevel=2
GOOGLE_APPLICATION_CREDENTIALS_DISABLED=true

# Python Settings
PYTHONUNBUFFERED=1

# Astra Bot Settings
ASTRA_LOG_LEVEL=INFO

# Discord Bot Settings (add your tokens)
# DISCORD_TOKEN=your_discord_token_here
# OPENAI_API_KEY=your_openai_key_here
# Add other API keys as needed
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("📄 Created .env file with optimal configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def main():
    """Main configuration process"""
    print("🌟 Astra Bot Environment Configuration")
    print("=" * 50)
    
    # Configure current environment
    configure_environment()
    
    # Create .env file for future runs
    create_env_file()
    
    print("\n🎉 Environment configuration complete!")
    print("💡 To use the .env file, install python-dotenv: pip install python-dotenv")
    print("💡 Then add 'from dotenv import load_dotenv; load_dotenv()' to your main bot file")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)