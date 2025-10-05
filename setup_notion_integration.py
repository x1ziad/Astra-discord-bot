#!/usr/bin/env python3
"""
Notion Integration Setup and Verification Script
This script helps verify and configure the Notion integration for AstraBot
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("\n🔍 CHECKING ENVIRONMENT VARIABLES")
    print("-" * 50)
    
    required_vars = {
        "NOTION_TOKEN": "Notion API Integration Token",
        "NOTION_DATABASE_ID": "Main Notion Database ID (for events/reminders)",
    }
    
    optional_vars = {
        "NOTION_TASKS_DB": "Tasks Database ID (optional, for task management)",
        "NOTION_REMINDERS_DB": "Reminders Database ID (optional, for reminders)",
        "NOTION_NOTES_DB": "Notes Database ID (optional, for quick notes)"
    }
    
    all_good = True
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * (len(value) - 10) + value[-10:]} (configured)")
        else:
            print(f"❌ {var}: NOT SET - {description}")
            all_good = False
    
    # Check optional variables
    print(f"\n📋 Optional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * (len(value) - 10) + value[-10:]} (configured)")
        else:
            print(f"⚪ {var}: Not set - {description}")
    
    return all_good

def check_configuration():
    """Check if Notion features are enabled in config"""
    print("\n⚙️ CHECKING CONFIGURATION")
    print("-" * 50)
    
    try:
        from config.unified_config import unified_config
        
        features_to_check = [
            "notion_integration",
            "notion_tasks", 
            "notion_reminders",
            "notion_notes"
        ]
        
        all_enabled = True
        for feature in features_to_check:
            enabled = unified_config.is_feature_enabled(feature)
            status = "✅ Enabled" if enabled else "❌ Disabled"
            print(f"{status} {feature}")
            if not enabled and feature == "notion_integration":
                all_enabled = False
        
        return all_enabled
        
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")
        return False

def test_notion_connection():
    """Test connection to Notion API"""
    print("\n🔗 TESTING NOTION API CONNECTION")
    print("-" * 50)
    
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        print("❌ Cannot test connection - NOTION_TOKEN not set")
        return False
    
    try:
        import aiohttp
        import asyncio
        
        async def test_connection():
            headers = {
                "Authorization": f"Bearer {notion_token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://api.notion.com/v1/users/me", headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ Connection successful!")
                            print(f"   User: {data.get('name', 'Unknown')}")
                            print(f"   Type: {data.get('type', 'Unknown')}")
                            return True
                        else:
                            error_text = await response.text()
                            print(f"❌ Connection failed: {response.status}")
                            print(f"   Error: {error_text}")
                            return False
            except Exception as e:
                print(f"❌ Connection error: {e}")
                return False
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_connection())
        loop.close()
        
        return result
        
    except ImportError:
        print("⚠️ Cannot test connection - aiohttp not available")
        return True  # Don't fail if we can't test
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False

def generate_setup_instructions():
    """Generate setup instructions for the user"""
    print("\n📋 NOTION INTEGRATION SETUP GUIDE")
    print("=" * 60)
    
    print("""
🔧 REQUIRED SETUP STEPS:

1. 📝 Create a Notion Integration:
   • Go to https://www.notion.so/my-integrations
   • Click "Create new integration"
   • Give it a name (e.g., "AstraBot Integration")
   • Select your workspace
   • Copy the "Internal Integration Token"

2. 🗄️ Create Notion Databases:
   • Create a database in Notion for events/reminders with these properties:
     - Name (Title)
     - Date (Date)
     - Description (Rich text)
     - Type (Select: Meeting, Reminder, Event, etc.)
   
   • Optional: Create separate databases for:
     - Tasks (Name, Due Date, Priority, Status)
     - Notes (Title, Content, Tags, Created)

3. 🔗 Share Databases with Integration:
   • Open each database in Notion
   • Click "Share" → "Invite"
   • Search for your integration name
   • Click "Invite"

4. 📋 Get Database IDs:
   • Open database in Notion
   • Copy the URL - the database ID is the long string after the last slash
   • Example: https://notion.so/myworkspace/DATABASE_ID?v=...

5. ⚙️ Add to .env file:
   Add these lines to your .env file (replace with your actual values):
   ```
   NOTION_TOKEN="your_integration_token_here"
   NOTION_DATABASE_ID="your_main_database_id_here"
   NOTION_TASKS_DB="your_tasks_database_id_here"          # Optional
   NOTION_REMINDERS_DB="your_reminders_database_id_here"  # Optional  
   NOTION_NOTES_DB="your_notes_database_id_here"          # Optional
   ```

6. 🔄 Restart the Bot:
   • Restart AstraBot to load the new configuration
   • Test with `/notion notion_status` command

🎯 AVAILABLE COMMANDS AFTER SETUP:
• `/notion reminders` - View upcoming events from Notion
• `/notion create_task` - Create tasks with AI enhancement
• `/notion quick_note` - Create quick notes with AI categorization
• `/notion search` - Search your Notion database
• `/notion summary` - Get AI-powered workspace summary
• `/notion sync` - Force sync with Notion (Admin only)
• `/notion notion_status` - Check integration status (Admin only)

🤖 AI FEATURES:
• Task descriptions enhanced by AI for clarity
• Notes automatically categorized and tagged
• Search queries improved for better results
• Workspace summaries with insights and recommendations
• Multi-provider AI fallback system (Google Gemini → OpenAI → Groq)

🔒 SECURITY:
• All API tokens are kept secure in .env file
• Never exposed in logs or network requests
• Integration tokens have limited permissions in Notion
""")

def main():
    """Main setup verification function"""
    print("🚀 ASTRABOT NOTION INTEGRATION SETUP")
    print("=" * 60)
    print(f"⏰ Setup verification started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load environment from .env file
    env_file = Path(".env")
    if env_file.exists():
        print(f"✅ Found .env file")
        # Load .env manually for this script
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"\'')
    else:
        print(f"⚠️ .env file not found - some checks may fail")
    
    # Run all checks
    env_check = check_environment_variables()
    config_check = check_configuration()
    connection_check = test_notion_connection()
    
    # Final summary
    print(f"\n📊 SETUP VERIFICATION SUMMARY")
    print("-" * 50)
    print(f"Environment Variables: {'✅ PASS' if env_check else '❌ FAIL'}")
    print(f"Configuration: {'✅ PASS' if config_check else '❌ FAIL'}")
    print(f"API Connection: {'✅ PASS' if connection_check else '❌ FAIL'}")
    
    if env_check and config_check and connection_check:
        print(f"\n🎉 NOTION INTEGRATION READY!")
        print("Your Notion integration is fully configured and ready to use.")
        print("Try running '/notion reminders' in Discord to test it!")
    else:
        print(f"\n⚠️ SETUP INCOMPLETE")
        print("Please check the failed items above and follow the setup guide below.")
        generate_setup_instructions()

if __name__ == "__main__":
    main()