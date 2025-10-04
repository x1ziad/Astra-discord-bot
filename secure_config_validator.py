#!/usr/bin/env python3
"""
Secure Configuration Validator
Ensures API keys are properly secured and not exposed in public repositories
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any


class ConfigValidator:
    """Validates and secures configuration files"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.sensitive_patterns = [
            r"sk-[a-zA-Z0-9-_]{40,}",  # OpenAI API keys
            r"[A-Za-z0-9]{24}\.[A-Za-z0-9]{6}\.[A-Za-z0-9-_]{27}",  # Discord tokens
            r"xoxb-[0-9]+-[0-9]+-[0-9]+-[a-fA-F0-9]{32}",  # Slack tokens
            r"AIza[0-9A-Za-z-_]{35}",  # Google API keys
        ]

    def load_config_with_env_substitution(self) -> Dict[str, Any]:
        """Load config with environment variable substitution"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            config_text = f.read()

        # Substitute environment variables
        def env_substitute(match):
            env_var = match.group(1)
            default_value = match.group(2) if match.group(2) else ""
            return os.getenv(env_var, default_value)

        # Pattern: ${VAR_NAME} or ${VAR_NAME:default_value}
        config_text = re.sub(
            r"\$\{([^}:]+)(?::([^}]*))?\}", env_substitute, config_text
        )

        return json.loads(config_text)

    def validate_no_exposed_secrets(self) -> Dict[str, Any]:
        """Validate that no sensitive information is exposed"""
        issues = []

        if not self.config_path.exists():
            return {"valid": True, "issues": []}

        with open(self.config_path, "r") as f:
            content = f.read()

        # Check for exposed API keys or tokens
        for pattern in self.sensitive_patterns:
            matches = re.findall(pattern, content)
            if matches:
                issues.append(
                    f"Found {len(matches)} potential API key(s) exposed in config"
                )

        # Check for non-placeholder values that look like keys
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if any(keyword in line.lower() for keyword in ["token", "api_key", "key"]):
                if not any(
                    placeholder in line
                    for placeholder in ["${", "YOUR_", "your_", "placeholder"]
                ):
                    if ":" in line and not line.strip().startswith("#"):
                        # Extract the value part
                        value_part = line.split(":", 1)[1].strip().strip('",')
                        if len(value_part) > 10 and not value_part.startswith("${"):
                            issues.append(
                                f"Line {i}: Potential exposed secret - {line.strip()}"
                            )

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "total_issues": len(issues),
        }

    def create_env_template(self) -> str:
        """Create a .env template from the current config"""
        try:
            config = json.loads(self.config_path.read_text())
            env_vars = []

            def extract_env_vars(obj, prefix=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if (
                            isinstance(value, str)
                            and value.startswith("${")
                            and value.endswith("}")
                        ):
                            env_var = value[2:-1]  # Remove ${ and }
                            env_vars.append(f"{env_var}=your_{env_var.lower()}_here")
                        elif isinstance(value, (dict, list)):
                            extract_env_vars(
                                value,
                                (
                                    f"{prefix}{key.upper()}_"
                                    if prefix
                                    else f"{key.upper()}_"
                                ),
                            )

            extract_env_vars(config)
            return "\n".join(sorted(set(env_vars)))

        except Exception as e:
            return f"# Error generating template: {e}"


def main():
    """Main security validation"""
    validator = ConfigValidator()

    print("🔒 Configuration Security Validation")
    print("=" * 40)

    # Check for exposed secrets
    validation = validator.validate_no_exposed_secrets()

    if validation["valid"]:
        print("✅ Configuration is secure - no exposed secrets found")
    else:
        print("❌ Security issues found:")
        for issue in validation["issues"]:
            print(f"   - {issue}")

    # Test environment variable substitution
    try:
        config = validator.load_config_with_env_substitution()
        print("✅ Configuration loads successfully with environment variables")
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")

    print("\n📝 Environment variables needed:")
    print(validator.create_env_template())


if __name__ == "__main__":
    main()
