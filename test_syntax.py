#!/usr/bin/env python3
"""
Quick syntax and import validation for AI components
"""

import ast
import sys
from pathlib import Path


def test_python_syntax(file_path):
    """Test if a Python file has valid syntax"""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Parse the AST to check syntax
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Test syntax of key files"""
    print("🔍 Python Syntax Validation")
    print("=" * 40)

    test_files = [
        "ai/consolidated_ai_engine.py",
        "cogs/advanced_ai.py",
        "config/enhanced_config.py",
        "config/config_manager.py",
    ]

    all_valid = True

    for file_path in test_files:
        path = Path(file_path)
        if path.exists():
            valid, error = test_python_syntax(file_path)
            if valid:
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path}: {error}")
                all_valid = False
        else:
            print(f"   ❓ {file_path}: File not found")
            all_valid = False

    print(
        f"\n📊 Syntax Check: {'✅ All files valid' if all_valid else '❌ Some files have issues'}"
    )

    return all_valid


if __name__ == "__main__":
    main()
