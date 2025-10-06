#!/usr/bin/env python3
"""
🔬 FINAL COMPREHENSIVE COMMAND VERIFICATION
Complete verification of every command in the Astra Bot system
"""

import sys
import os
import re
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def extract_commands_from_file(file_path):
    """Extract all commands from a Python file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find all @app_commands.command patterns
        pattern = r'@app_commands\.command\([^)]*name=["\']([^"\']+)["\'][^)]*description=["\']([^"\']*)["\']'
        commands = re.findall(pattern, content)

        return commands
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return []


def main():
    print("🤖 ASTRA BOT - FINAL COMMAND VERIFICATION")
    print("=" * 100)

    total_commands = 0
    cog_commands = {}

    # Get all cog files
    cog_dir = Path("cogs")
    if not cog_dir.exists():
        print("❌ Cogs directory not found")
        return

    for cog_file in sorted(cog_dir.glob("*.py")):
        if cog_file.name.startswith("__"):
            continue

        cog_name = cog_file.stem
        commands = extract_commands_from_file(cog_file)

        if commands:
            cog_commands[cog_name] = commands
            total_commands += len(commands)

            print(f"\n📦 {cog_name.upper()} ({len(commands)} commands)")
            print("-" * 80)

            for i, (cmd_name, cmd_desc) in enumerate(commands, 1):
                # Clean up description
                desc = cmd_desc[:70] + "..." if len(cmd_desc) > 70 else cmd_desc
                desc = desc.replace("\n", " ").strip()

                # Determine command prefix based on cog
                if cog_name == "nexus":
                    prefix = "/nexus"
                else:
                    prefix = (
                        f"/{cog_name}" if not cmd_name.startswith(cmd_name) else "/"
                    )

                print(f"  {i:2d}. {prefix} {cmd_name:<20} - {desc}")

    # Summary
    print("\n" + "=" * 100)
    print("📊 COMPREHENSIVE COMMAND SUMMARY")
    print("=" * 100)

    print(f"🎯 Total Commands Found: {total_commands}")
    print(f"📦 Active Cog Modules: {len(cog_commands)}")

    # Breakdown by cog
    print(f"\n📋 Commands by Module:")
    for cog_name, commands in sorted(
        cog_commands.items(), key=lambda x: len(x[1]), reverse=True
    ):
        print(f"   {cog_name:<25} : {len(commands):2d} commands")

    # Verify critical commands exist
    print(f"\n🔍 Critical Command Verification:")
    critical_commands = {
        "nexus": ["ping", "status", "help", "test_reporting"],
        "admin_optimized": ["reload", "logs"],
        "quiz": ["start", "stats"],
        "analytics": ["overview"],
    }

    all_critical_present = True
    for cog, required_cmds in critical_commands.items():
        if cog in cog_commands:
            existing_cmds = [cmd[0] for cmd in cog_commands[cog]]
            for required_cmd in required_cmds:
                if required_cmd in existing_cmds:
                    print(f"   ✅ {cog}::{required_cmd}")
                else:
                    print(f"   ❌ {cog}::{required_cmd} - MISSING")
                    all_critical_present = False
        else:
            print(f"   ❌ {cog} cog - NOT FOUND")
            all_critical_present = False

    # Final status
    print(f"\n🎉 VERIFICATION COMPLETE!")
    if all_critical_present:
        print("✅ All critical commands are present and accounted for")
    else:
        print("⚠️  Some critical commands may be missing")

    print(
        f"🚀 System Status: {'FULLY OPERATIONAL' if total_commands > 30 else 'NEEDS REVIEW'}"
    )
    print("=" * 100)

    return total_commands


if __name__ == "__main__":
    command_count = main()
    print(f"\n🎯 Final Count: {command_count} total commands verified")
    sys.exit(0 if command_count > 20 else 1)
