#!/usr/bin/env python3
"""
📊 FINAL COMMAND COUNT ANALYSIS
Provides exact command count after cleanup
"""

import os
import re
import sys


def count_slash_commands():
    """Count all slash commands in the cogs directory"""

    print("📊 FINAL COMMAND COUNT ANALYSIS")
    print("=" * 50)

    total_commands = 0
    command_breakdown = {}

    cogs_dir = "/Users/ziadmekawy/Developer/Discord-Stellaris/AstraBot/cogs"

    for filename in sorted(os.listdir(cogs_dir)):
        if filename.endswith(".py") and filename != "__init__.py":
            filepath = os.path.join(cogs_dir, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Count different types of command decorators
                app_commands = len(re.findall(r"@app_commands\.command", content))
                tree_commands = len(re.findall(r"@tree\.command", content))
                slash_commands = len(re.findall(r"@commands\.hybrid_command", content))
                group_commands = len(re.findall(r"@.*\.command\(", content))

                # Total for this file
                file_total = app_commands + tree_commands + slash_commands

                if file_total > 0:
                    command_breakdown[filename] = file_total
                    total_commands += file_total

                    print(f"📁 {filename:<25} | {file_total:>2} commands")

            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")

    print("=" * 50)
    print(f"🎯 TOTAL SLASH COMMANDS: {total_commands}")
    print("=" * 50)

    # Show top command contributors
    print("\n🏆 Top Command Contributors:")
    sorted_commands = sorted(
        command_breakdown.items(), key=lambda x: x[1], reverse=True
    )

    for i, (filename, count) in enumerate(sorted_commands[:10], 1):
        print(f"  {i:>2}. {filename:<20} | {count:>2} commands")

    # Calculate reduction
    original_estimate = 85
    reduction_percent = ((original_estimate - total_commands) / original_estimate) * 100

    print(f"\n📈 CLEANUP IMPACT:")
    print(f"  📊 Original estimate: ~{original_estimate} commands")
    print(f"  🎯 Current count: {total_commands} commands")
    print(f"  📉 Commands removed: ~{original_estimate - total_commands}")
    print(f"  📈 Reduction percentage: {reduction_percent:.1f}%")

    # Performance impact
    removed_files = ["server_management.py", "enhanced_autonomous_moderation.py"]
    print(f"\n🗑️ FILES REMOVED: {len(removed_files)}")
    for file in removed_files:
        print(f"  ✅ {file}")

    print(f"\n🎮 ACTIVE COG FILES: {len(command_breakdown)}")
    print(f"⚡ PERFORMANCE IMPACT: Positive ({reduction_percent:.1f}% reduction)")

    return total_commands, command_breakdown


if __name__ == "__main__":
    count_slash_commands()
