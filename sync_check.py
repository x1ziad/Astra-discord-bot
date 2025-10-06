#!/usr/bin/env python3
"""
🔄 COMPREHENSIVE SYSTEM SYNCHRONIZATION CHECK
Ensures all components are properly aligned and synchronized
"""

import sys
import os
import importlib
import traceback
import inspect
from pathlib import Path
import subprocess

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class SystemSynchronizer:
    def __init__(self):
        self.results = {
            "files_sync": {"passed": [], "failed": []},
            "imports_sync": {"passed": [], "failed": []},
            "bot_config": {"passed": [], "failed": []},
            "cog_references": {"passed": [], "failed": []},
            "command_integrity": {"passed": [], "failed": []},
        }

    def print_header(self, title):
        print(f"\n{'='*80}")
        print(f"🔄 {title}")
        print("=" * 80)

    def print_section(self, title):
        print(f"\n📋 {title}")
        print("-" * 60)

    def check_file_integrity(self):
        """Check all files exist and are properly structured"""
        self.print_section("FILE INTEGRITY CHECK")

        critical_files = [
            "bot.1.0.py",
            "cogs/nexus.py",
            "config/unified_config.py",
            "utils/database.py",
            "ai/universal_ai_client.py",
            ".env",
        ]

        for file_path in critical_files:
            if Path(file_path).exists():
                try:
                    # Check if Python files compile
                    if file_path.endswith(".py"):
                        subprocess.run(
                            ["python", "-m", "py_compile", file_path],
                            check=True,
                            capture_output=True,
                        )
                    print(f"✅ {file_path}")
                    self.results["files_sync"]["passed"].append(file_path)
                except Exception as e:
                    print(f"❌ {file_path}: Syntax error - {str(e)}")
                    self.results["files_sync"]["failed"].append((file_path, str(e)))
            else:
                print(f"❌ {file_path}: File not found")
                self.results["files_sync"]["failed"].append(
                    (file_path, "File not found")
                )

    def check_import_synchronization(self):
        """Check all imports are properly synchronized"""
        self.print_section("IMPORT SYNCHRONIZATION")

        # Test critical imports
        imports_to_test = [
            ("discord", "Discord.py library"),
            ("config.unified_config", "Bot configuration"),
            ("utils.database", "Database utilities"),
            ("cogs.nexus", "NEXUS control system"),
            ("ai.universal_ai_client", "AI client system"),
        ]

        for module_name, description in imports_to_test:
            try:
                importlib.import_module(module_name)
                print(f"✅ {description}")
                self.results["imports_sync"]["passed"].append(module_name)
            except Exception as e:
                print(f"❌ {description}: {str(e)}")
                self.results["imports_sync"]["failed"].append((module_name, str(e)))

    def check_bot_config_sync(self):
        """Check bot configuration synchronization"""
        self.print_section("BOT CONFIGURATION SYNC")

        try:
            # Check bot.1.0.py for proper cog loading
            with open("bot.1.0.py", "r") as f:
                bot_content = f.read()

            # Check if removed cogs are still referenced
            removed_cogs = ["cogs.help", "cogs.utilities", "cogs.stats"]
            for cog in removed_cogs:
                if cog in bot_content:
                    print(f"❌ {cog}: Still referenced in bot file")
                    self.results["bot_config"]["failed"].append(
                        (cog, "Still referenced")
                    )
                else:
                    print(f"✅ {cog}: Properly removed")
                    self.results["bot_config"]["passed"].append(cog)

            # Check if NEXUS is properly loaded
            if "cogs.nexus" in bot_content:
                print("✅ NEXUS: Properly referenced in bot loading")
                self.results["bot_config"]["passed"].append("nexus_loading")
            else:
                print("❌ NEXUS: Missing from bot loading")
                self.results["bot_config"]["failed"].append(
                    ("nexus_loading", "Missing reference")
                )

        except Exception as e:
            print(f"❌ Bot config check failed: {e}")
            self.results["bot_config"]["failed"].append(("bot_config", str(e)))

    def check_cog_references(self):
        """Check all cog references are synchronized"""
        self.print_section("COG REFERENCE SYNCHRONIZATION")

        # Get all actual cog files
        cog_dir = Path("cogs")
        actual_cogs = [
            f.stem for f in cog_dir.glob("*.py") if not f.name.startswith("__")
        ]

        print(f"📦 Found {len(actual_cogs)} cog files:")
        for cog in sorted(actual_cogs):
            print(f"   • {cog}")

        # Check bot.1.0.py loading configuration
        try:
            with open("bot.1.0.py", "r") as f:
                content = f.read()

            # Find all cog references in extension loading
            import re

            cog_references = re.findall(r'"cogs\.([^"]+)"', content)

            print(f"\n🔗 Found {len(cog_references)} cog references in bot file:")
            for cog_ref in sorted(set(cog_references)):
                if cog_ref in actual_cogs:
                    print(f"   ✅ {cog_ref}")
                    self.results["cog_references"]["passed"].append(cog_ref)
                else:
                    print(f"   ❌ {cog_ref}: File not found")
                    self.results["cog_references"]["failed"].append(
                        (cog_ref, "File not found")
                    )

        except Exception as e:
            print(f"❌ Cog reference check failed: {e}")
            self.results["cog_references"]["failed"].append(("cog_check", str(e)))

    def check_command_integrity(self):
        """Check command integrity and count"""
        self.print_section("COMMAND INTEGRITY CHECK")

        try:
            # Import and check NEXUS
            from cogs.nexus import NexusControlSystem

            # Count commands using inspection
            methods = inspect.getmembers(
                NexusControlSystem, predicate=inspect.isfunction
            )

            # Look for app_commands decorators in the source
            import ast

            with open("cogs/nexus.py", "r") as f:
                tree = ast.parse(f.read())

            command_count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and any(
                    isinstance(decorator, ast.Attribute)
                    and getattr(decorator.attr, "", "") == "command"
                    for decorator in node.decorator_list
                ):
                    command_count += 1

            print(f"✅ NEXUS Commands: {command_count} found")
            self.results["command_integrity"]["passed"].append(
                f"nexus_commands_{command_count}"
            )

            # Verify essential commands exist
            essential_commands = ["ping", "status", "info", "health", "help"]
            nexus_source = open("cogs/nexus.py", "r").read()

            for cmd in essential_commands:
                if f'name="{cmd}"' in nexus_source:
                    print(f"✅ Essential command: {cmd}")
                    self.results["command_integrity"]["passed"].append(f"cmd_{cmd}")
                else:
                    print(f"❌ Essential command missing: {cmd}")
                    self.results["command_integrity"]["failed"].append(
                        (f"cmd_{cmd}", "Missing")
                    )

        except Exception as e:
            print(f"❌ Command integrity check failed: {e}")
            self.results["command_integrity"]["failed"].append(
                ("command_check", str(e))
            )

    def check_environment_sync(self):
        """Check environment synchronization"""
        self.print_section("ENVIRONMENT SYNCHRONIZATION")

        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, "r") as f:
                env_content = f.read()

            required_vars = ["OWNER_ID", "DISCORD_TOKEN", "MISTRAL_API_KEY"]
            for var in required_vars:
                if var in env_content and f"{var}=" in env_content:
                    print(f"✅ {var}: Configured")
                    self.results["bot_config"]["passed"].append(f"env_{var}")
                else:
                    print(f"❌ {var}: Missing or misconfigured")
                    self.results["bot_config"]["failed"].append(
                        (f"env_{var}", "Missing")
                    )
        else:
            print("❌ .env file not found")
            self.results["bot_config"]["failed"].append((".env", "File not found"))

    def generate_sync_report(self):
        """Generate comprehensive synchronization report"""
        self.print_header("SYNCHRONIZATION REPORT")

        total_checks = 0
        total_passed = 0
        total_failed = 0

        for category, results in self.results.items():
            passed = len(results["passed"])
            failed = len(results["failed"])
            total = passed + failed

            if total > 0:
                total_checks += total
                total_passed += passed
                total_failed += failed

                success_rate = (passed / total) * 100
                status = (
                    "✅" if success_rate == 100 else "⚠️" if success_rate >= 80 else "❌"
                )

                print(
                    f"{status} {category.upper().replace('_', ' ')}: {passed}/{total} ({success_rate:.1f}%)"
                )

                # Show critical failures
                if results["failed"]:
                    for item, error in results["failed"][:3]:  # Show first 3 failures
                        print(f"   ❌ {item}: {error}")

        print(f"\n{'='*80}")
        overall_success = (total_passed / total_checks) * 100 if total_checks > 0 else 0
        status_emoji = (
            "🎉" if overall_success >= 95 else "✅" if overall_success >= 85 else "⚠️"
        )

        print(
            f"{status_emoji} OVERALL SYNCHRONIZATION: {total_passed}/{total_checks} ({overall_success:.1f}%)"
        )
        print(f"📊 Checks Passed: {total_passed}")
        print(f"❌ Issues Found: {total_failed}")

        if overall_success >= 90:
            print("🚀 SYSTEM STATUS: READY FOR REPOSITORY UPDATE")
        elif overall_success >= 75:
            print("⚠️ SYSTEM STATUS: NEEDS MINOR FIXES BEFORE UPDATE")
        else:
            print("🚨 SYSTEM STATUS: CRITICAL ISSUES - UPDATE NOT RECOMMENDED")

        print("=" * 80)

        return overall_success >= 85

    def run_full_sync_check(self):
        """Run complete synchronization check"""
        self.print_header("COMPREHENSIVE SYSTEM SYNCHRONIZATION")

        self.check_file_integrity()
        self.check_import_synchronization()
        self.check_bot_config_sync()
        self.check_cog_references()
        self.check_command_integrity()
        self.check_environment_sync()

        return self.generate_sync_report()


if __name__ == "__main__":
    synchronizer = SystemSynchronizer()
    success = synchronizer.run_full_sync_check()
    sys.exit(0 if success else 1)
