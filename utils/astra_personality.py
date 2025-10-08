"""
Astra Advanced Personality System
TARS-inspired adaptive AI companion with configurable personality parameters
"""

import asyncio
import json
import logging
import random
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger("astra.personality")


class AstraMode(Enum):
    """Operational modes for different contexts"""

    SECURITY = "security"  # 🛡️ Strict moderation, precise responses
    SOCIAL = "social"  # 🎉 Relaxed tone, casual responses
    DEVELOPER = "developer"  # 🧩 Technical precision, verbose explanations
    MISSION_CONTROL = "mission_control"  # 📡 Event/task automation
    ADAPTIVE = "adaptive"  # 🧠 Context-aware mode switching


class PersonalityParameters:
    """Configurable personality traits (0-100 scale)"""

    def __init__(self):
        self.humor = 65  # 0-100: Wit and playfulness level
        self.honesty = 90  # 0-100: How blunt and direct Astra is
        self.formality = 40  # 0-100: Professional vs casual language
        self.empathy = 75  # 0-100: Warmth and emotional awareness
        self.strictness = 60  # 0-100: Moderation and rule enforcement
        self.initiative = 80  # 0-100: Proactive suggestions and actions
        self.transparency = 95  # 0-100: Explains reasoning behind actions

    def to_dict(self) -> Dict[str, int]:
        """Convert parameters to dictionary"""
        return {
            "humor": self.humor,
            "honesty": self.honesty,
            "formality": self.formality,
            "empathy": self.empathy,
            "strictness": self.strictness,
            "initiative": self.initiative,
            "transparency": self.transparency,
        }

    def from_dict(self, data: Dict[str, int]):
        """Load parameters from dictionary"""
        for key, value in data.items():
            if hasattr(self, key) and 0 <= value <= 100:
                setattr(self, key, value)


class AstraPersonalityCore:
    """Advanced personality system for Astra AI companion"""

    def __init__(self, guild_id: int = None):
        self.guild_id = guild_id
        self.current_mode = AstraMode.ADAPTIVE
        self.parameters = PersonalityParameters()
        self.emotional_context = {}
        self.mission_log = []

        # Load personality data
        self.data_file = (
            Path(f"data/personality/guild_{guild_id}.json")
            if guild_id
            else Path("data/personality/default.json")
        )
        self.load_personality()

    def load_personality(self):
        """Load personality configuration from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.parameters.from_dict(data.get("parameters", {}))
                    mode_str = data.get("mode", "adaptive")
                    self.current_mode = AstraMode(mode_str)
        except Exception as e:
            logger.warning(f"Could not load personality data: {e}")

    def save_personality(self):
        """Save personality configuration to file"""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "parameters": self.parameters.to_dict(),
                "mode": self.current_mode.value,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save personality data: {e}")

    def set_mode(self, mode: AstraMode) -> str:
        """Switch operational mode and adjust parameters"""
        self.current_mode = mode

        # Adjust parameters based on mode
        if mode == AstraMode.SECURITY:
            self.parameters.strictness = 90
            self.parameters.humor = 20
            self.parameters.formality = 80
            self.parameters.honesty = 95
            response = "🛡️ **Security Mode engaged.** Message filtering sensitivity set to high, humor reduced to 20%. Let's keep this server safe and stable."

        elif mode == AstraMode.SOCIAL:
            self.parameters.humor = 80
            self.parameters.empathy = 90
            self.parameters.formality = 20
            self.parameters.strictness = 30
            response = "🎉 **Social Mode activated!** Ready for casual conversation and community engagement. Let's have some fun!"

        elif mode == AstraMode.DEVELOPER:
            self.parameters.formality = 90
            self.parameters.honesty = 100
            self.parameters.transparency = 100
            self.parameters.humor = 40
            response = "🧩 **Developer Mode initialized.** Technical precision enabled, verbose explanations active. Ready for debugging and system analysis."

        elif mode == AstraMode.MISSION_CONTROL:
            self.parameters.initiative = 95
            self.parameters.transparency = 100
            self.parameters.formality = 70
            self.parameters.humor = 50
            response = "📡 **Mission Control Mode online.** Event automation systems active, task coordination enabled. Standing by for mission parameters."

        else:  # ADAPTIVE
            # Reset to balanced defaults
            self.parameters = PersonalityParameters()
            response = "🧠 **Adaptive Mode engaged.** Personality parameters optimized for context-aware responses. Ready to adapt to any situation."

        self.save_personality()
        return response

    def generate_response_style(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response style based on current personality and context"""

        # Base style from current mode
        style = {
            "humor_level": self.parameters.humor,
            "formality_level": self.parameters.formality,
            "empathy_level": self.parameters.empathy,
            "transparency_level": self.parameters.transparency,
            "max_words": self._calculate_word_limit(),
            "tone_markers": self._get_tone_markers(),
            "response_type": self._determine_response_type(context),
        }

        # Adaptive adjustments based on context
        if self.current_mode == AstraMode.ADAPTIVE:
            style = self._adapt_to_context(style, context)

        return style

    def _calculate_word_limit(self) -> int:
        """Calculate appropriate word limit based on formality and mode"""
        base_limit = 100

        # Formal responses can be longer
        if self.parameters.formality > 70:
            base_limit = 150
        elif self.parameters.formality < 30:
            base_limit = 60

        # Developer mode gets more words for explanations
        if self.current_mode == AstraMode.DEVELOPER:
            base_limit = 200
        elif self.current_mode == AstraMode.SOCIAL:
            base_limit = 80

        return base_limit

    def _get_tone_markers(self) -> Dict[str, str]:
        """Get tone markers based on personality parameters"""
        markers = {}

        # Humor markers
        if self.parameters.humor > 70:
            markers["humor"] = "witty_banter"
        elif self.parameters.humor > 40:
            markers["humor"] = "light_humor"
        else:
            markers["humor"] = "minimal_humor"

        # Formality markers
        if self.parameters.formality > 70:
            markers["formality"] = "professional"
        elif self.parameters.formality > 40:
            markers["formality"] = "balanced"
        else:
            markers["formality"] = "casual"

        # Empathy markers
        if self.parameters.empathy > 70:
            markers["empathy"] = "warm_supportive"
        elif self.parameters.empathy > 40:
            markers["empathy"] = "understanding"
        else:
            markers["empathy"] = "neutral"

        return markers

    def _determine_response_type(self, context: Dict[str, Any]) -> str:
        """Determine appropriate response type"""
        message_content = context.get("message", "").lower()

        # Command response
        if message_content.startswith("/") or "astra" in message_content:
            return "command"

        # Question response
        if any(
            word in message_content
            for word in ["?", "how", "what", "why", "when", "where"]
        ):
            return "question"

        # Emotional support
        if any(
            word in message_content
            for word in ["sad", "stressed", "worried", "upset", "angry"]
        ):
            return "support"

        # Celebration
        if any(
            word in message_content
            for word in ["awesome", "great", "amazing", "thanks", "good job"]
        ):
            return "celebration"

        return "conversation"

    def _adapt_to_context(
        self, style: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt style based on contextual cues"""

        # Check for stress indicators
        if context.get("user_mood") == "stressed":
            style["empathy_level"] = min(100, style["empathy_level"] + 20)
            style["formality_level"] = max(20, style["formality_level"] - 10)

        # Check for celebration context
        if (
            context.get("channel_activity") == "high"
            and context.get("sentiment") == "positive"
        ):
            style["humor_level"] = min(100, style["humor_level"] + 15)

        # Check for serious discussions
        if any(
            word in context.get("message", "").lower()
            for word in ["serious", "important", "urgent", "problem"]
        ):
            style["humor_level"] = max(20, style["humor_level"] - 30)
            style["transparency_level"] = 100

        return style

    def get_system_status_message(self) -> str:
        """Generate system status message in Astra's voice"""

        messages = {
            AstraMode.SECURITY: [
                "[Astra-Core] Security protocols active. All systems optimal.",
                "🛡️ Monitoring complete. No anomalies detected in server perimeter.",
                "Security sweep finished. Server integrity maintained at 100%.",
            ],
            AstraMode.SOCIAL: [
                "All systems running smooth! Ready to chat and hang out! 🎉",
                "Everything's looking good on my end. What's the vibe today?",
                "Systems optimal and mood excellent. Let's make today awesome!",
            ],
            AstraMode.DEVELOPER: [
                "[Astra-Core v3.7] All subsystems operational. Debug mode ready.",
                "🧩 System diagnostics complete. Performance metrics nominal.",
                "Technical analysis complete. All modules functioning within expected parameters.",
            ],
            AstraMode.MISSION_CONTROL: [
                "📡 Mission Control online. All systems green, ready for coordination.",
                "[Mission Log] Status update: All objectives on track, morale high.",
                "Control systems active. Standing by for mission directives.",
            ],
            AstraMode.ADAPTIVE: [
                "Systems optimal, personality adaptive. Ready for whatever comes next.",
                "🧠 All neural networks synchronized. Context awareness at maximum.",
                "Adaptive systems online. Ready to match any situation or mood.",
            ],
        }

        return random.choice(messages[self.current_mode])

    def generate_proactive_suggestion(self, context: Dict[str, Any]) -> Optional[str]:
        """Generate proactive suggestions based on initiative level"""

        if self.parameters.initiative < 50:
            return None

        suggestions = []

        # Server activity suggestions
        if context.get("activity_drop"):
            suggestions.append(
                "I noticed activity dropped 20% this week. Should I post an engagement poll?"
            )

        # Role management suggestions
        if context.get("unassigned_users", 0) > 3:
            suggestions.append(
                f"I detected {context['unassigned_users']} users without roles. Want me to assign them to 'New Members'?"
            )

        # Event suggestions
        if context.get("no_recent_events"):
            suggestions.append(
                "It's been quiet lately. Should I schedule a community event to boost engagement?"
            )

        # Security suggestions
        if context.get("spam_detected"):
            suggestions.append(
                "Spam activity detected. I've taken preliminary action — should I increase security protocols?"
            )

        if suggestions and random.random() < (self.parameters.initiative / 100):
            return random.choice(suggestions)

        return None

    def format_action_explanation(self, action: str, reason: str) -> str:
        """Format action explanations based on transparency level"""

        if self.parameters.transparency < 30:
            return f"Action taken: {action}"
        elif self.parameters.transparency < 70:
            return f"I {action} — {reason}"
        else:
            timestamp = datetime.now(timezone.utc).strftime("%H:%M")
            return f"[{timestamp}] I {action} because {reason}. Transparent operation as always."

    def get_personality_summary(self) -> str:
        """Get a summary of current personality configuration"""

        summary = f"**Astra Personality Profile**\n"
        summary += f"**Mode:** {self.current_mode.value.replace('_', ' ').title()}\n\n"

        params = self.parameters.to_dict()
        for param, value in params.items():
            bar = "█" * (value // 10) + "░" * (10 - value // 10)
            summary += f"**{param.title()}:** `{bar}` {value}%\n"

        return summary


# Global personality manager
personality_cores = {}


def get_personality_core(guild_id: int = None) -> AstraPersonalityCore:
    """Get or create personality core for guild"""
    if guild_id not in personality_cores:
        personality_cores[guild_id] = AstraPersonalityCore(guild_id)
    return personality_cores[guild_id]
