#!/usr/bin/env python3
"""
Quick fix script for indentation errors in disabled functions
"""

import os
import re
from pathlib import Path


def fix_disabled_function_patterns(file_path):
    """Fix common patterns of disabled functions with indentation errors"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Pattern 1: Fix @commands.Cog.listener() followed by # async def pattern
    pattern1 = r'(\s*)@commands\.Cog\.listener\(\)\s*\n\s*# async def ([^:]+):\s*\n\s*"""([^"]+)"""\s*\n'
    replacement1 = (
        r'\1# @commands.Cog.listener()\n\1# async def \2:\n\1#     """\3"""\n'
    )
    content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)

    # Pattern 2: Fix lines that should be commented but aren't
    lines = content.split("\n")
    in_disabled_function = False
    fixed_lines = []

    for i, line in enumerate(lines):
        # Check if we're starting a disabled function
        if "# async def on_message(" in line or "# async def on_member_" in line:
            in_disabled_function = True
            fixed_lines.append(line)
            continue

        # Check if we're ending a disabled function
        if (
            in_disabled_function
            and line.strip()
            and not line.startswith("    #")
            and not line.startswith("#")
        ):
            # If this line starts with @ or def or class, we're out of the disabled function
            if (
                line.strip().startswith("@")
                or line.strip().startswith("def ")
                or line.strip().startswith("class ")
            ):
                in_disabled_function = False
                fixed_lines.append(line)
                continue
            # Otherwise, this line should be commented
            if line.strip():
                # Get the indentation level
                indent = len(line) - len(line.lstrip())
                if indent >= 4:  # Should be part of the function
                    commented_line = line[:4] + "#" + line[4:]
                    fixed_lines.append(commented_line)
                else:
                    in_disabled_function = False
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        else:
            fixed_lines.append(line)

    content = "\n".join(fixed_lines)

    # Only write if content changed
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    # Files that need fixing based on test results
    problem_files = [
        "cogs/security_commands.py",
        "cogs/ai_companion.py",
        "cogs/ai_moderation.py",
        "cogs/analytics.py",
    ]

    project_root = Path(__file__).parent

    for file_path in problem_files:
        full_path = project_root / file_path
        if full_path.exists():
            try:
                if fix_disabled_function_patterns(full_path):
                    print(f"✅ Fixed: {file_path}")
                else:
                    print(f"ℹ️  No changes needed: {file_path}")
            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")


if __name__ == "__main__":
    main()
