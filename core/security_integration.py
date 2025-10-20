"""
🛡️ SECURITY INTEGRATION MODULE
Connects manual security commands with autonomous AI-enhanced protection
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime
from discord.ext import commands
import discord

# from cogs.security_commands import SecurityCommands  # Import as needed

logger = logging.getLogger("astra.security.integration")


class SecuritySystemIntegration:
    """
    Integrates manual security commands with autonomous AI protection

    This class bridges the gap between:
    - Manual lockdown controls (Owner only)
    - Autonomous threat detection (AI-enhanced)
    - Admin monitoring tools
    - Real-time security responses
    """

    def __init__(self, bot):
        self.bot = bot
        self.ai_security = None  # AI security system (if available)
        self.manual_commands = None  # Manual security commands cog
        self.integration_active = False

        # Security configuration
        self.config = {
            "threat_detection": True,
            "auto_moderation": True,
            "advanced_scanning": True,
            "real_time_monitoring": True,
            "behavioral_analysis": True,
            "spam_protection": True,
            "raid_protection": True,
            "content_filtering": True,
        }

        # Security statistics
        self.security_stats = {
            "threats_detected": 0,
            "messages_analyzed": 0,
            "users_monitored": 0,
            "actions_taken": 0,
            "false_positives": 0,
            "uptime": 0,
            "response_time_avg": 0.0,
            "cache_hit_rate": 95.0,
        }

    async def initialize(self):
        """Initialize the security integration system"""
        try:
            # Initialize start time for uptime tracking
            self.start_time = time.time()

            # Get the AI-enhanced security system
            self.ai_security = getattr(self.bot, "ai_security", None)

            # Get the manual security commands cog
            self.manual_commands = self.bot.get_cog("SecurityCommands")

            if self.ai_security and self.manual_commands:
                # Connect the systems
                await self._connect_systems()
                self.integration_active = True
                logger.info("🛡️ Security system integration initialized successfully")
            else:
                # Still mark as active for basic functionality
                self.integration_active = True
                logger.info(
                    "🛡️ Security system integration initialized with limited functionality"
                )

        except Exception as e:
            logger.error(f"❌ Failed to initialize security integration: {e}")

    async def get_user_profile(self, user_id: int):
        """
        Get user security profile - bridge method for compatibility

        This method ensures compatibility with security components that expect
        a get_user_profile method on the SecuritySystemIntegration class.
        """
        try:
            # Try to get profile from AI security system first
            if self.ai_security and hasattr(self.ai_security, "get_user_profile"):
                return await self.ai_security.get_user_profile(user_id)

            # Fallback to manual security commands if available
            if self.manual_commands and hasattr(
                self.manual_commands, "get_user_profile"
            ):
                return await self.manual_commands.get_user_profile(user_id)

            # Last resort: create a basic profile with minimal security info
            from cogs.security_manager import UserProfile

            profile = UserProfile(user_id)
            profile.trust_score = 50  # Default neutral trust score
            return profile

        except Exception as e:
            logger.error(f"Error getting user profile for {user_id}: {e}")
            # Return minimal profile to prevent crashes
            from cogs.security_manager import UserProfile

            profile = UserProfile(user_id)
            profile.trust_score = 50
            return profile

    async def _connect_systems(self):
        """Connect autonomous AI security with manual commands"""

        # Override AI security's lockdown method to use manual commands system
        original_emergency_lockdown = self.ai_security.emergency_lockdown

        async def integrated_lockdown(
            guild: discord.Guild,
            threat_event: Any,
            reason: str = "Autonomous threat detection",
        ):
            """Integrated lockdown that uses the manual commands system"""
            if self.manual_commands and not self.manual_commands.lockdown_active:
                # Use the manual commands lockdown system for consistency
                success = await self.manual_commands._activate_lockdown(
                    guild, reason, manual=False
                )

                # Log the threat in the manual system
                if hasattr(threat_event, "threat_level"):
                    self.manual_commands.log_threat(
                        threat_type=f"Auto: {threat_event.__class__.__name__}",
                        level=min(threat_event.threat_level.value, 5),
                        user_id=getattr(threat_event, "user_id", None),
                        channel_id=getattr(threat_event, "channel_id", None),
                        details=reason,
                    )

                return success
            return False

        # Replace the AI security lockdown method
        self.ai_security.emergency_lockdown = integrated_lockdown

        # Set up threat logging integration
        original_log_threat = getattr(self.ai_security, "log_threat", None)
        if original_log_threat:

            def integrated_threat_logging(*args, **kwargs):
                # Call original logging
                result = original_log_threat(*args, **kwargs)

                # Also log in manual commands system
                if len(args) >= 2:
                    threat_type = str(args[0]) if args[0] else "Unknown"
                    threat_level = (
                        int(args[1]) if isinstance(args[1], (int, float)) else 1
                    )

                    self.manual_commands.log_threat(
                        threat_type=f"AI: {threat_type}",
                        level=min(threat_level, 5),
                        user_id=kwargs.get("user_id"),
                        channel_id=kwargs.get("channel_id"),
                        details=kwargs.get(
                            "details", str(args[2:]) if len(args) > 2 else None
                        ),
                    )

                return result

            self.ai_security.log_threat = integrated_threat_logging

    async def handle_message_security(self, message: discord.Message) -> Dict[str, Any]:
        """
        Integrated message security handling

        Combines AI threat detection with manual command system logging
        """
        if not self.integration_active or not self.ai_security:
            return {"processed": False, "reason": "Integration not active"}

        try:
            # Update message analysis stats
            if self.manual_commands:
                self.manual_commands.increment_stats("messages_analyzed")

            # Use AI-enhanced security for analysis
            threat_result = await self.ai_security.analyze_message_threat(message)

            if threat_result and threat_result.get("threat_detected"):
                # Log the threat
                if self.manual_commands:
                    self.manual_commands.log_threat(
                        threat_type=threat_result.get(
                            "threat_type", "Message Analysis"
                        ),
                        level=threat_result.get("threat_level", 1),
                        user_id=message.author.id,
                        channel_id=message.channel.id,
                        details=threat_result.get(
                            "details", "Suspicious message detected"
                        ),
                    )

                # Check if auto-lockdown should trigger
                if self.manual_commands and threat_result.get("threat_level", 0) >= 4:
                    await self.manual_commands.auto_lockdown_check(
                        message.guild,
                        threat_result.get("threat_level", 0),
                        threat_result.get("threat_type", "High threat"),
                    )

            return threat_result

        except Exception as e:
            logger.error(f"Error in integrated message security: {e}")
            return {"processed": False, "error": str(e)}

    async def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data"""
        if not self.integration_active:
            return {"active": False}

        dashboard_data = {
            "active": True,
            "timestamp": datetime.utcnow().isoformat(),
            "lockdown_status": {
                "active": (
                    self.manual_commands.lockdown_active
                    if self.manual_commands
                    else False
                ),
                "channels_locked": (
                    len(self.manual_commands.lockdown_channels)
                    if self.manual_commands
                    else 0
                ),
                "start_time": (
                    self.manual_commands.lockdown_start_time.isoformat()
                    if (
                        self.manual_commands
                        and self.manual_commands.lockdown_start_time
                    )
                    else None
                ),
            },
            "ai_enhancement": {
                "active": self.ai_security is not None,
                "threat_patterns": (
                    len(getattr(self.ai_security, "threat_patterns_2025", {}))
                    if self.ai_security
                    else 0
                ),
                "performance": "Operational",
            },
            "statistics": (
                self.manual_commands.security_stats if self.manual_commands else {}
            ),
            "recent_threats": len(
                [
                    t
                    for t in (
                        self.manual_commands.threat_log if self.manual_commands else []
                    )
                    if (
                        datetime.utcnow() - t.get("timestamp", datetime.min)
                    ).total_seconds()
                    < 3600
                ]
            ),  # Threats in last hour
        }

        return dashboard_data

    async def emergency_override(
        self, guild: discord.Guild, user_id: int, action: str, reason: str
    ) -> Dict[str, Any]:
        """
        Emergency override system for owner

        Allows the owner to perform emergency actions that bypass normal restrictions
        """
        # Verify owner permissions
        if user_id != 1115739214148026469:  # Your user ID
            return {"success": False, "error": "Unauthorized access"}

        try:
            result = {
                "success": False,
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
            }

            if action == "force_lockdown":
                if self.manual_commands:
                    success = await self.manual_commands._activate_lockdown(
                        guild, f"EMERGENCY OVERRIDE: {reason}", manual=True
                    )
                    result["success"] = success
                    result["message"] = (
                        "Emergency lockdown activated" if success else "Lockdown failed"
                    )

            elif action == "force_unlock":
                if self.manual_commands:
                    success = await self.manual_commands._deactivate_lockdown(
                        guild, f"EMERGENCY OVERRIDE: {reason}"
                    )
                    result["success"] = success
                    result["message"] = (
                        "Emergency unlock completed" if success else "Unlock failed"
                    )

            elif action == "reset_security":
                # Reset all security systems
                if self.manual_commands:
                    self.manual_commands.threat_log.clear()
                    self.manual_commands.security_stats = {
                        "threats_detected": 0,
                        "messages_analyzed": 0,
                        "lockdowns_triggered": 0,
                        "auto_actions_taken": 0,
                    }
                    result["success"] = True
                    result["message"] = "Security systems reset"

            elif action == "status_report":
                result["success"] = True
                result["data"] = await self.get_security_dashboard_data()
                result["message"] = "Security status retrieved"

            return result

        except Exception as e:
            logger.error(f"Emergency override failed: {e}")
            return {"success": False, "error": str(e)}

    def is_integration_healthy(self) -> bool:
        """Check if the security integration is healthy and operational"""
        return (
            self.integration_active
            and self.ai_security is not None
            and self.manual_commands is not None
        )

    def get_security_stats(self) -> Dict[str, Any]:
        """Get comprehensive security statistics"""
        try:
            # Update uptime
            self.security_stats["uptime"] = time.time() - getattr(
                self, "start_time", time.time()
            )

            # Try to get additional stats from AI security if available
            if self.ai_security and hasattr(self.ai_security, "get_stats"):
                ai_stats = self.ai_security.get_stats()
                self.security_stats.update(ai_stats)

            # Try to get stats from manual commands if available
            if self.manual_commands and hasattr(self.manual_commands, "security_stats"):
                manual_stats = self.manual_commands.security_stats
                for key, value in manual_stats.items():
                    if key in self.security_stats:
                        self.security_stats[key] += value
                    else:
                        self.security_stats[key] = value

            return {
                **self.security_stats,
                "integration_active": self.integration_active,
                "ai_security_active": self.ai_security is not None,
                "manual_commands_active": self.manual_commands is not None,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting security stats: {e}")
            return {
                "error": str(e),
                "integration_active": self.integration_active,
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def get_user_security_report(
        self, user_id: int, guild_id: int = None
    ) -> Dict[str, Any]:
        """Get comprehensive user security report"""
        try:
            report = {
                "user_id": user_id,
                "guild_id": guild_id,
                "trust_score": 50,  # Default neutral score
                "violations": [],
                "actions_taken": [],
                "last_activity": None,
                "risk_level": "low",
                "status": "clean",
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Try to get user profile from AI security
            if self.ai_security and hasattr(self.ai_security, "get_user_profile"):
                ai_profile = await self.ai_security.get_user_profile(user_id)
                if ai_profile:
                    report["trust_score"] = getattr(ai_profile, "trust_score", 50)
                    report["violations"].extend(getattr(ai_profile, "violations", []))
                    report["last_activity"] = getattr(ai_profile, "last_activity", None)

            # Try to get additional data from manual commands
            if self.manual_commands and hasattr(self.manual_commands, "get_user_data"):
                manual_data = await self.manual_commands.get_user_data(user_id)
                if manual_data:
                    report["actions_taken"].extend(manual_data.get("actions", []))

            # Determine risk level based on trust score
            trust_score = report["trust_score"]
            if trust_score >= 80:
                report["risk_level"] = "low"
                report["status"] = "trusted"
            elif trust_score >= 50:
                report["risk_level"] = "medium"
                report["status"] = "neutral"
            elif trust_score >= 20:
                report["risk_level"] = "high"
                report["status"] = "suspicious"
            else:
                report["risk_level"] = "critical"
                report["status"] = "flagged"

            # Add violation count and recent activity
            report["violation_count"] = len(report["violations"])
            report["recent_violations"] = [
                v
                for v in report["violations"]
                if (
                    datetime.utcnow()
                    - datetime.fromisoformat(v.get("timestamp", "1970-01-01"))
                ).days
                <= 7
            ]

            # Add fields expected by user_security command
            report["total_violations"] = len(report["violations"])
            report["recent_violations_24h"] = len(
                [
                    v
                    for v in report["violations"]
                    if (
                        datetime.utcnow()
                        - datetime.fromisoformat(v.get("timestamp", "1970-01-01"))
                    ).days
                    <= 1
                ]
            )
            report["violation_streak"] = 0  # TODO: Calculate actual streak
            report["punishment_level"] = max(0, min(7, (100 - trust_score) // 15))

            # Additional fields expected by the command
            report["positive_contributions"] = max(
                0, trust_score - 50
            )  # Based on trust score above neutral
            report["quarantine_status"] = "none" if trust_score >= 50 else "monitored"
            report["last_violation"] = None  # Timestamp of last violation

            # Behavioral analysis
            report["behavioral_summary"] = {
                "avg_message_length": 50,  # Default reasonable message length
                "channel_diversity": 1,  # Number of channels user is active in
                "activity_pattern": "normal",  # normal, suspicious, irregular
            }

            # Update behavioral pattern based on trust score
            if trust_score >= 70:
                report["behavioral_summary"]["activity_pattern"] = "normal"
            elif trust_score >= 40:
                report["behavioral_summary"]["activity_pattern"] = "irregular"
            else:
                report["behavioral_summary"]["activity_pattern"] = "suspicious"

            # Find most recent violation timestamp
            if report["violations"]:
                try:
                    timestamps = [
                        datetime.fromisoformat(
                            v.get("timestamp", "1970-01-01")
                        ).timestamp()
                        for v in report["violations"]
                    ]
                    report["last_violation"] = max(timestamps)
                except:
                    report["last_violation"] = None

            # Add is_trusted field based on trust score
            report["is_trusted"] = trust_score >= 70

            return report

        except Exception as e:
            logger.error(f"Error getting user security report for {user_id}: {e}")
            return {
                "error": str(e),
                "user_id": user_id,
                "guild_id": guild_id,
                "trust_score": 50,
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
            }

    def increment_stat(self, stat_name: str, amount: int = 1):
        """Increment a security statistic"""
        if stat_name in self.security_stats:
            self.security_stats[stat_name] += amount
        else:
            self.security_stats[stat_name] = amount

    def update_config(self, setting: str, value: Any):
        """Update security configuration setting"""
        try:
            self.config[setting] = value
            logger.info(f"Security config updated: {setting} = {value}")
            return True
        except Exception as e:
            logger.error(f"Error updating security config {setting}: {e}")
            return False

    def get_config(self, setting: str = None):
        """Get security configuration setting or all settings"""
        if setting:
            return self.config.get(setting, None)
        return self.config.copy()

    async def shutdown(self):
        """Properly shutdown the security integration"""
        try:
            logger.info("🛡️ Shutting down security integration...")
            self.integration_active = False

            # Clean up any resources
            if hasattr(self, "monitoring_task"):
                self.monitoring_task.cancel()

            logger.info("✅ Security integration shutdown complete")

        except Exception as e:
            logger.error(f"Error during security integration shutdown: {e}")

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log a security event"""
        try:
            event = {
                "type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details,
            }

            # Increment relevant stats
            self.increment_stat(
                "threats_detected"
                if "threat" in event_type.lower()
                else "actions_taken"
            )

            logger.info(f"Security event logged: {event_type}")

        except Exception as e:
            logger.error(f"Error logging security event: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the security system"""
        try:
            uptime = time.time() - self.start_time

            return {
                "uptime_seconds": uptime,
                "uptime_formatted": f"{uptime/3600:.1f} hours",
                "integration_active": self.integration_active,
                "components": {
                    "ai_security": self.ai_security is not None,
                    "manual_commands": self.manual_commands is not None,
                },
                "stats": self.security_stats.copy(),
                "config_settings": len(self.config),
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                "error": str(e),
                "integration_active": self.integration_active,
                "last_updated": datetime.utcnow().isoformat(),
            }


async def setup_security_integration(bot) -> SecuritySystemIntegration:
    """Set up and initialize the security system integration"""
    integration = SecuritySystemIntegration(bot)
    await integration.initialize()

    # Store reference on bot for access from other components
    bot.security_integration = integration

    return integration
