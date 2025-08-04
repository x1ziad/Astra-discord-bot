#!/usr/bin/env python3
"""
Astra Bot - Pre-Deployment Validation Script
Validates all components are ready for Railway deployment
"""

import asyncio
import json
import os
import sys
from pathlib import Path


# Color codes for output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'='*60}{Colors.END}\n")


def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}📋 {text}{Colors.END}")
    print(f"{Colors.CYAN}{'-'*50}{Colors.END}")


def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


class ValidationResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.errors = []

    def add_pass(self, message):
        self.passed += 1
        print_success(message)

    def add_fail(self, message):
        self.failed += 1
        self.errors.append(message)
        print_error(message)

    def add_warning(self, message):
        self.warnings += 1
        print_warning(message)


def validate_file_structure():
    """Validate required files exist"""
    print_section("File Structure Validation")
    result = ValidationResult()

    required_files = [
        "bot.1.0.py",
        "requirements.txt",
        "config.json",
        "railway.toml",
        "Dockerfile",
        "config/railway_config.py",
        "RAILWAY_DEPLOYMENT.md",
    ]

    required_dirs = ["cogs", "config"]

    # Check files
    for file_path in required_files:
        if Path(file_path).exists():
            result.add_pass(f"Required file exists: {file_path}")
        else:
            result.add_fail(f"Missing required file: {file_path}")

    # Check directories
    for dir_path in required_dirs:
        if Path(dir_path).is_dir():
            result.add_pass(f"Required directory exists: {dir_path}")
        else:
            result.add_fail(f"Missing required directory: {dir_path}")

    return result


def validate_config_files():
    """Validate configuration files"""
    print_section("Configuration Validation")
    result = ValidationResult()

    # Validate config.json
    try:
        with open("config.json", "r") as f:
            config = json.load(f)

        if "discord" in config:
            result.add_pass("Discord configuration section found")
        else:
            result.add_fail("Missing discord configuration section")

        if "openai" in config:
            result.add_pass("OpenAI configuration section found")
        else:
            result.add_fail("Missing openai configuration section")

    except FileNotFoundError:
        result.add_fail("config.json not found")
    except json.JSONDecodeError as e:
        result.add_fail(f"Invalid JSON in config.json: {e}")

    # Validate railway.toml
    try:
        with open("railway.toml", "r") as f:
            railway_config = f.read()

        required_vars = ["DISCORD_TOKEN", "OPENAI_API_KEY", "DISCORD_CLIENT_ID"]
        for var in required_vars:
            if var in railway_config:
                result.add_pass(f"Railway environment variable configured: {var}")
            else:
                result.add_fail(f"Missing Railway environment variable: {var}")

    except FileNotFoundError:
        result.add_fail("railway.toml not found")

    return result


def validate_requirements():
    """Validate requirements.txt"""
    print_section("Dependencies Validation")
    result = ValidationResult()

    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()

        required_packages = [
            "discord.py",
            "openai",
            "aiohttp",
            "aiosqlite",
            "python-dotenv",
            "psutil",
        ]

        for package in required_packages:
            if package in requirements:
                result.add_pass(f"Required package found: {package}")
            else:
                result.add_fail(f"Missing required package: {package}")

    except FileNotFoundError:
        result.add_fail("requirements.txt not found")

    return result


def validate_cogs():
    """Validate cog files"""
    print_section("Cogs Validation")
    result = ValidationResult()

    required_cogs = [
        "help.py",
        "notion.py",
        "quiz.py",
        "roles.py",
        "space.py",
        "stats.py",
        "advanced_ai.py",
        "admin.py",
    ]

    for cog in required_cogs:
        cog_path = Path(f"cogs/{cog}")
        if cog_path.exists():
            result.add_pass(f"Cog file exists: {cog}")

            # Basic syntax check
            try:
                with open(cog_path, "r") as f:
                    content = f.read()

                if "class" in content and "commands.Cog" in content:
                    result.add_pass(f"Cog properly structured: {cog}")
                else:
                    result.add_warning(f"Cog may not be properly structured: {cog}")

            except Exception as e:
                result.add_fail(f"Error reading cog {cog}: {e}")
        else:
            result.add_fail(f"Missing cog file: {cog}")

    return result


def validate_docker():
    """Validate Dockerfile"""
    print_section("Docker Configuration Validation")
    result = ValidationResult()

    try:
        with open("Dockerfile", "r") as f:
            dockerfile = f.read()

        required_elements = [
            "FROM python:3.12-slim",
            "COPY requirements.txt",
            "RUN pip install",
            "COPY . .",
            'CMD ["python", "bot.1.0.py"]',
            "HEALTHCHECK",
        ]

        for element in required_elements:
            if element in dockerfile:
                result.add_pass(f"Dockerfile contains: {element}")
            else:
                result.add_fail(f"Dockerfile missing: {element}")

    except FileNotFoundError:
        result.add_fail("Dockerfile not found")

    return result


def validate_main_bot():
    """Validate main bot file"""
    print_section("Main Bot File Validation")
    result = ValidationResult()

    try:
        with open("bot.1.0.py", "r") as f:
            bot_code = f.read()

        required_imports = [
            "import discord",
            "from discord.ext import commands",
            "import openai",
            "import asyncio",
        ]

        for imp in required_imports:
            if imp in bot_code:
                result.add_pass(f"Required import found: {imp}")
            else:
                result.add_fail(f"Missing required import: {imp}")

        # Check for Railway configuration integration
        if "railway_config" in bot_code:
            result.add_pass("Railway configuration integration found")
        else:
            result.add_warning("Railway configuration integration not found")

        # Check for OpenAI configuration
        if "openai" in bot_code.lower():
            result.add_pass("OpenAI integration found")
        else:
            result.add_fail("OpenAI integration not found")

    except FileNotFoundError:
        result.add_fail("bot.1.0.py not found")

    return result


async def main():
    """Run all validations"""
    print_header("🚄 ASTRA BOT - RAILWAY DEPLOYMENT VALIDATION")

    print_info("Validating bot components for Railway deployment...")
    print_info("This will check all files, configurations, and dependencies.")

    # Run all validations
    validations = [
        validate_file_structure(),
        validate_config_files(),
        validate_requirements(),
        validate_cogs(),
        validate_docker(),
        validate_main_bot(),
    ]

    # Calculate totals
    total_passed = sum(v.passed for v in validations)
    total_failed = sum(v.failed for v in validations)
    total_warnings = sum(v.warnings for v in validations)

    # Print summary
    print_section("Validation Summary")

    if total_failed == 0:
        print_success(f"✅ ALL VALIDATIONS PASSED! ({total_passed} checks)")
        if total_warnings > 0:
            print_warning(f"⚠️  {total_warnings} warnings (non-critical)")
        print_info("\n🚀 Your bot is ready for Railway deployment!")
        print_info("📖 Next steps:")
        print_info("   1. Push your code to GitHub")
        print_info("   2. Connect GitHub repo to Railway")
        print_info("   3. Set environment variables in Railway dashboard")
        print_info("   4. Deploy and enjoy 24/7 bot operation!")

    else:
        print_error(
            f"❌ VALIDATION FAILED ({total_failed} errors, {total_passed} passed)"
        )
        print_info("\n🔧 Errors that need fixing:")
        for validation in validations:
            for error in validation.errors:
                print(f"   • {error}")

        print_info("\n💡 Please fix these issues before deploying to Railway.")

    # Print deployment readiness
    readiness_score = (
        (total_passed / (total_passed + total_failed)) * 100
        if (total_passed + total_failed) > 0
        else 0
    )

    print_section("Deployment Readiness")
    if readiness_score >= 95:
        print(
            f"{Colors.GREEN}🎯 Readiness Score: {readiness_score:.1f}% - EXCELLENT{Colors.END}"
        )
    elif readiness_score >= 80:
        print(
            f"{Colors.YELLOW}🎯 Readiness Score: {readiness_score:.1f}% - GOOD{Colors.END}"
        )
    else:
        print(
            f"{Colors.RED}🎯 Readiness Score: {readiness_score:.1f}% - NEEDS WORK{Colors.END}"
        )

    print_header("VALIDATION COMPLETE")

    return total_failed == 0


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Validation failed with error: {e}")
        sys.exit(1)
