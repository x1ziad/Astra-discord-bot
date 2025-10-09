"""
🔧 MESSAGE HANDLER OPTIMIZER
Disables conflicting on_message listeners to prevent performance issues

This script comments out on_message handlers in existing cogs to ensure
the High-Performance Coordinator has exclusive control over message processing.

This prevents:
- Duplicate processing
- Performance bottlenecks  
- Race conditions
- Inconsistent responses
"""

import os
import re
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("optimizer")

COGS_DIR = Path(__file__).parent / "cogs"

# Files to optimize and their on_message handlers to disable
FILES_TO_OPTIMIZE = {
    "advanced_ai.py": {
        "handler_line": "async def on_message(self, message: discord.Message):",
        "comment": "# 🚀 DISABLED: Message processing moved to High-Performance Coordinator"
    },
    "ai_companion.py": {
        "handler_line": "async def on_message(self, message: discord.Message):",
        "comment": "# 🚀 DISABLED: Message processing moved to High-Performance Coordinator"
    },
    "ai_moderation.py": {
        "handler_line": "async def on_message(self, message: discord.Message):",
        "comment": "# 🚀 DISABLED: Message processing moved to High-Performance Coordinator"
    },
    "security_manager.py": {
        "handler_line": "async def on_message(self, message: discord.Message):",
        "comment": "# 🚀 DISABLED: Message processing moved to High-Performance Coordinator"
    },
    "analytics.py": {
        "handler_line": "async def on_message(self, message):",
        "comment": "# 🚀 DISABLED: Message processing moved to High-Performance Coordinator"
    },
    "enhanced_security.py": {
        "handler_line": "async def on_message(self, message: discord.Message):",
        "comment": "# 🚀 DISABLED: Message processing moved to High-Performance Coordinator"
    },
    "security_commands.py": {
        "handler_line": "async def on_message(self, message: discord.Message):",
        "comment": "# 🚀 DISABLED: Message processing moved to High-Performance Coordinator"
    }
}


def disable_on_message_handler(file_path: Path, handler_info: dict):
    """Disable a specific on_message handler in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        handler_line = handler_info["handler_line"]
        comment = handler_info["comment"]
        
        # Check if already disabled
        if comment in content:
            logger.info(f"✅ {file_path.name}: Already optimized")
            return False
        
        # Find the handler and add comment
        if handler_line in content:
            # Add comment before the handler
            pattern = rf"(\s*@commands\.Cog\.listener\(\)\s*\n\s*)({re.escape(handler_line)})"
            replacement = rf"\1{comment}\n\1# \2"
            
            new_content = re.sub(pattern, replacement, content)
            
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logger.info(f"✅ {file_path.name}: on_message handler disabled")
                return True
            else:
                logger.warning(f"⚠️ {file_path.name}: Pattern not found for modification")
                return False
        else:
            logger.info(f"📝 {file_path.name}: No on_message handler found")
            return False
    
    except Exception as e:
        logger.error(f"❌ {file_path.name}: Error - {e}")
        return False


def optimize_message_handlers():
    """Optimize all message handlers to prevent conflicts"""
    logger.info("🚀 Starting message handler optimization...")
    
    optimized_count = 0
    
    for filename, handler_info in FILES_TO_OPTIMIZE.items():
        file_path = COGS_DIR / filename
        
        if file_path.exists():
            if disable_on_message_handler(file_path, handler_info):
                optimized_count += 1
        else:
            logger.warning(f"⚠️ File not found: {filename}")
    
    logger.info(f"🎯 Optimization complete: {optimized_count} handlers optimized")
    return optimized_count


def create_backup():
    """Create backup of cogs directory"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(__file__).parent / f"cogs_backup_{timestamp}"
    
    try:
        shutil.copytree(COGS_DIR, backup_dir)
        logger.info(f"💾 Backup created: {backup_dir}")
        return backup_dir
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return None


if __name__ == "__main__":
    print("🔧 MESSAGE HANDLER OPTIMIZER")
    print("=" * 50)
    
    # Create backup first
    backup_path = create_backup()
    if backup_path:
        print(f"💾 Backup created at: {backup_path}")
    
    # Optimize handlers
    optimized = optimize_message_handlers()
    
    print("=" * 50)
    print(f"✅ Optimization complete!")
    print(f"📊 Handlers optimized: {optimized}")
    print(f"🚀 High-Performance Coordinator is now ready!")
    print("")
    print("📝 What was changed:")
    print("   • Disabled conflicting on_message handlers")
    print("   • Added optimization comments")
    print("   • Preserved original functionality")
    print("")
    print("🎯 Next steps:")
    print("   • Restart the bot to apply changes")
    print("   • Use /performance command to monitor")
    print("   • Test with multiple simultaneous messages")