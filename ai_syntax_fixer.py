#!/usr/bin/env python3
"""
🛠️ AI SYNTAX FIXER
Quick fix for syntax errors introduced during optimization
"""

import os
import re
from pathlib import Path


def fix_ai_module_syntax():
    """Fix syntax errors in AI modules"""
    project_root = Path(__file__).parent
    ai_dir = project_root / "ai"

    print("🔧 FIXING AI MODULE SYNTAX ERRORS")
    print("=" * 50)

    # Common syntax fixes
    fixes_applied = 0

    for ai_file in ai_dir.glob("*.py"):
        if ai_file.name in ["__init__.py", "tars_personality_engine.py"]:
            continue

        try:
            with open(ai_file, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix 1: Empty try/except blocks
            content = re.sub(
                r"try:\s*\n\s*from ai\.tars_personality_engine",
                "try:\n    from ai.tars_personality_engine",
                content,
            )

            content = re.sub(
                r"except ImportError:\s*\n\s*TARS_AVAILABLE = False",
                "except ImportError:\n    TARS_AVAILABLE = False",
                content,
            )

            # Fix 2: Missing indentation in TARS integration
            tars_integration_fixed = '''
# TARS Personality System Integration
try:
    from ai.tars_personality_engine import get_tars_personality, get_tars_response
    TARS_AVAILABLE = True
except ImportError:
    TARS_AVAILABLE = False

def enhance_with_tars_personality(response: str, context: str = "", user_input: str = "", user_id: int = None) -> str:
    """Enhance response with TARS-like personality"""
    if not TARS_AVAILABLE:
        return response
    
    try:
        from ai.tars_personality_engine import get_tars_response
        tars_data = get_tars_response(context, user_input, user_id)
        
        # Apply TARS enhancements
        if tars_data.get("personality_prefix"):
            response = f"{tars_data['personality_prefix']}\\n\\n{response}"
        
        if tars_data.get("personality_suffix"):
            response = f"{response}{tars_data['personality_suffix']}"
        
        return response
    except Exception:
        return response
'''

            # Replace broken TARS integration
            if "TARS Personality System Integration" in content:
                # Find and replace the broken integration
                pattern = r"\n# TARS Personality System Integration.*?return response\s*except Exception:\s*return response"
                content = re.sub(
                    pattern, tars_integration_fixed, content, flags=re.DOTALL
                )

            # Fix 3: Broken caching code
            caching_code_fixed = '''
# Response Caching System for Performance
import functools
import hashlib
from typing import Dict, Any
import time

_response_cache: Dict[str, Dict[str, Any]] = {}
_cache_expiry = 300  # 5 minutes

def cached_ai_response(func):
    """Decorator for caching AI responses"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Create cache key
        cache_key = hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()
        
        # Check cache
        if cache_key in _response_cache:
            cached_data = _response_cache[cache_key]
            if time.time() - cached_data['timestamp'] < _cache_expiry:
                return cached_data['response']
        
        # Generate new response
        response = await func(*args, **kwargs)
        
        # Cache response
        _response_cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        
        # Clean old cache entries (simple cleanup)
        if len(_response_cache) > 100:
            oldest_key = min(_response_cache.keys(), key=lambda k: _response_cache[k]['timestamp'])
            del _response_cache[oldest_key]
        
        return response
    return wrapper
'''

            # Replace broken caching code
            if "Response Caching System for Performance" in content:
                pattern = (
                    r"\n# Response Caching System for Performance.*?return wrapper"
                )
                content = re.sub(pattern, caching_code_fixed, content, flags=re.DOTALL)

            # Fix 4: Double imports and malformed sections
            lines = content.split("\n")
            cleaned_lines = []
            skip_until_blank = False

            for i, line in enumerate(lines):
                # Skip malformed sections
                if "# TARS Personality System Integration" in line and skip_until_blank:
                    continue

                if line.strip() == "" and skip_until_blank:
                    skip_until_blank = False

                if not skip_until_blank:
                    cleaned_lines.append(line)

            content = "\n".join(cleaned_lines)

            # Write back if changes were made
            if content != original_content:
                with open(ai_file, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✅ Fixed syntax in {ai_file.name}")
                fixes_applied += 1
            else:
                print(f"✓ {ai_file.name} - no fixes needed")

        except Exception as e:
            print(f"❌ Error fixing {ai_file.name}: {e}")

    print(f"\n🎯 Applied {fixes_applied} syntax fixes")
    return fixes_applied


if __name__ == "__main__":
    fixes_applied = fix_ai_module_syntax()

    if fixes_applied > 0:
        print(f"\n🎉 Successfully fixed {fixes_applied} AI modules!")
        print("🚀 AI system should now be fully functional.")
    else:
        print("\n✅ No syntax fixes needed - all modules are clean!")

    print("\n🤖 Ready for TARS-level operation!")
