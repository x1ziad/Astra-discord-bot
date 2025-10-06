#!/usr/bin/env python3
"""Script to fix all ViolationRecord constructor calls"""

import re

# Read the file
with open("core/unified_security_system.py", "r") as f:
    content = f.read()

# Pattern to match ViolationRecord calls
pattern = r"ViolationRecord\(\s*([^)]+)\)"


def fix_violation_record(match):
    """Fix individual ViolationRecord constructor"""
    args = match.group(1)

    # If it already uses create_violation_record, skip
    if "create_violation_record" in args:
        return match.group(0)

    # Simple replacement for now - convert to helper call
    return (
        f"self.create_violation_record(\n                    {args}\n                )"
    )


# Replace all ViolationRecord calls
fixed_content = re.sub(pattern, fix_violation_record, content, flags=re.DOTALL)

# Write back
with open("core/unified_security_system.py", "w") as f:
    f.write(fixed_content)

print("Fixed ViolationRecord constructor calls")
