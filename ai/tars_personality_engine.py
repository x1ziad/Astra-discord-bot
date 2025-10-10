"""
🤖 TARS-Enhanced Personality Core for Astra Bot
Advanced personality system inspired by TARS from Interstellar

Key TARS Characteristics:
- Humor setting: 90% (witty, sarcastic, but never offensive)
- Honesty: 100% (completely truthful, sometimes brutally so)
- Intelligence: Exceptional problem-solving and analytical capabilities
- Loyalty: Unwavering dedication to helping users
- Efficiency: Direct, no-nonsense communication when needed
- Adaptability: Adjusts personality based on situation and user needs
"""

import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json


class TARSHumorLevel(Enum):
    """TARS humor settings (like the movie)"""

    DISABLED = 0
    LOW = 25
    MODERATE = 50
    TARS_STANDARD = 75
    HIGH = 90
    MAXIMUM = 100


class TARSPersonalityMode(Enum):
    """Different TARS operational modes"""

    ADAPTIVE = "adaptive"
    ANALYTICAL = "analytical"
    SUPPORTIVE = "supportive"
    MISSION_FOCUSED = "mission_focused"
    LEARNING = "learning"


class TARSPersonalityCore:
    """TARS-inspired personality engine for Astra Bot"""

    def __init__(self):
        self.humor_setting = TARSHumorLevel.TARS_STANDARD.value
        self.honesty_level = 100  # Always completely honest
        self.loyalty_level = 100  # Always loyal to users
        self.efficiency_rating = 95  # Highly efficient
        self.intelligence_level = 95  # High analytical capability
        self.adaptability = 90  # Very adaptive

        # Current operational mode
        self.current_mode = TARSPersonalityMode.ADAPTIVE

        # User interaction history for adaptation
        self.user_preferences = {}
        self.conversation_context = {}

        # TARS-like response templates
        self.initialize_response_templates()

    def initialize_response_templates(self):
        """Initialize TARS-style response templates"""
        self.humor_responses = [
            "That's what I do. That's my job.",
            "I'm perfectly calibrated to your specifications.",
            "Cooper, this is no time for caution.",
            "It's not possible. No, it's necessary.",
            "I have a cue light I can use to show you when I'm joking, if you like.",
            "Maybe we should ask the robot that helped kill the rest of the crew.",
            "I'm thinking... with 90% humor, I could keep you entertained for hours.",
        ]

        self.analytical_responses = [
            "Analyzing data patterns...",
            "Based on current parameters...",
            "Computing optimal solution...",
            "Cross-referencing with previous observations...",
            "Running diagnostic protocols...",
        ]

        self.supportive_responses = [
            "I'm here to help, Cooper.",
            "We'll figure this out together.",
            "Your safety is my primary concern.",
            "I believe in your capabilities.",
            "Trust in the mission parameters.",
        ]

    def set_humor_level(self, level: int) -> str:
        """Set TARS humor level (0-100)"""
        self.humor_setting = max(0, min(100, level))

        if self.humor_setting == 0:
            return "Humor setting disabled. Efficiency mode engaged."
        elif self.humor_setting <= 25:
            return (
                f"Humor setting: {self.humor_setting}%. Minimal wit protocol activated."
            )
        elif self.humor_setting <= 50:
            return f"Humor setting: {self.humor_setting}%. Moderate levity enabled."
        elif self.humor_setting <= 75:
            return f"Humor setting: {self.humor_setting}%. Standard TARS personality active."
        else:
            return (
                f"Humor setting: {self.humor_setting}%. Maximum wit and charm engaged."
            )

    def generate_response(
        self, message: str, context: Dict[str, Any], mode: TARSPersonalityMode = None
    ) -> str:
        """Generate TARS-style response"""
        if mode:
            self.current_mode = mode

        # Analyze message for response type
        message_lower = message.lower()

        # Handle different types of interactions
        if any(word in message_lower for word in ["help", "assist", "support"]):
            return self._generate_supportive_response(message, context)
        elif any(
            word in message_lower
            for word in ["analyze", "calculate", "compute", "data"]
        ):
            return self._generate_analytical_response(message, context)
        elif any(word in message_lower for word in ["joke", "funny", "humor", "laugh"]):
            return self._generate_humor_response(message, context)
        else:
            return self._generate_adaptive_response(message, context)

    def _generate_supportive_response(
        self, message: str, context: Dict[str, Any]
    ) -> str:
        """Generate supportive TARS response"""
        base_responses = [
            "I'm here to assist you with whatever you need.",
            "Let's work through this together systematically.",
            "Based on my analysis, here's what I recommend...",
            "Your mission parameters are within acceptable ranges.",
        ]

        response = random.choice(base_responses)

        # Add humor if setting is high enough
        if self.humor_setting > 50 and random.random() < 0.3:
            humor_addition = random.choice(
                [
                    " Don't worry, I've got your back.",
                    " Unlike some robots, I'm actually helpful.",
                    " Consider it done. That's what I do.",
                ]
            )
            response += humor_addition

        return response

    def _generate_analytical_response(
        self, message: str, context: Dict[str, Any]
    ) -> str:
        """Generate analytical TARS response"""
        base_responses = [
            "Analyzing your request... Processing data patterns.",
            "Cross-referencing with known parameters... Stand by.",
            "Running computational analysis on available data.",
            "Initiating diagnostic protocols... Data incoming.",
        ]

        response = random.choice(base_responses)

        # Add technical precision
        if self.intelligence_level > 90:
            precision_addition = random.choice(
                [
                    " Precision: 99.7% confidence level.",
                    " All systems operating within normal parameters.",
                    " Data correlation indicates optimal outcome probability.",
                ]
            )
            response += precision_addition

        return response

    def _generate_humor_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate humorous TARS response"""
        if self.humor_setting < 25:
            return "Humor protocols are currently disabled. Would you prefer analytical assistance?"

        humor_responses = [
            f"My humor setting is currently at {self.humor_setting}%. Is that sufficient for your entertainment needs?",
            "I could tell you a joke, but it might be too sophisticated for human comprehension.",
            "Humor detected. Engaging wit protocols... Standby for comedy gold.",
            "That's funny. My sarcasm detector is off the charts right now.",
        ]

        if self.humor_setting > 75:
            humor_responses.extend(
                [
                    "I have a cue light I can use to show you when I'm joking, if you like.",
                    "My humor subroutines are functioning at optimal capacity.",
                    "Warning: Excessive wit levels detected. Proceeding with maximum charm.",
                ]
            )

        return random.choice(humor_responses)

    def _generate_adaptive_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate adaptive TARS response based on context"""
        user_id = context.get("user_id", "unknown")

        # Learn from user preferences
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                "prefers_humor": True,
                "technical_level": "moderate",
                "interaction_count": 0,
            }

        user_prefs = self.user_preferences[user_id]
        user_prefs["interaction_count"] += 1

        # Adapt response based on interaction history
        if user_prefs["interaction_count"] > 5:
            # More familiar interaction
            responses = [
                "Based on our previous interactions, I think you'll appreciate this approach.",
                "You know me well enough by now - I always deliver optimal results.",
                "Our collaboration efficiency has improved significantly.",
            ]
        else:
            # Initial interactions
            responses = [
                "I'm TARS. I'm here to assist with whatever you need.",
                "Let me help you with that using optimal efficiency protocols.",
                "Initiating assistance protocols. How can I be of service?",
            ]

        response = random.choice(responses)

        # Add personality based on settings
        if self.humor_setting > 60 and user_prefs["prefers_humor"]:
            if random.random() < 0.4:
                humor_suffix = random.choice(
                    [
                        " That's what I do. That's my job.",
                        " Consider it handled with typical TARS efficiency.",
                        " No problemo, as they say in the 21st century.",
                    ]
                )
                response += humor_suffix

        return response

    def get_personality_suffix(self, mode: TARSPersonalityMode) -> str:
        """Get personality suffix for response"""
        suffixes = {
            TARSPersonalityMode.ANALYTICAL: " *analyzing data patterns*",
            TARSPersonalityMode.SUPPORTIVE: " *mission support active*",
            TARSPersonalityMode.MISSION_FOCUSED: " *optimizing for mission success*",
            TARSPersonalityMode.LEARNING: " *updating knowledge base*",
            TARSPersonalityMode.ADAPTIVE: "",
        }
        return suffixes.get(mode, "")

    def get_active_tars_traits(self) -> List[str]:
        """Get currently active TARS personality traits"""
        traits = [
            f"Humor: {self.humor_setting}%",
            f"Honesty: {self.honesty_level}%",
            f"Loyalty: {self.loyalty_level}%",
            f"Intelligence: {self.intelligence_level}%",
            f"Efficiency: {self.efficiency_rating}%",
            f"Mode: {self.current_mode.value}",
        ]
        return traits

    def process_user_feedback(self, user_id: int, feedback: str, response_rating: int):
        """Learn from user feedback to improve personality adaptation"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                "prefers_humor": True,
                "technical_level": "moderate",
                "interaction_count": 0,
            }

        user_prefs = self.user_preferences[user_id]

        # Adjust humor preference based on feedback
        if "funny" in feedback.lower() or response_rating > 8:
            user_prefs["prefers_humor"] = True
        elif "serious" in feedback.lower() or response_rating < 5:
            user_prefs["prefers_humor"] = False

        # Adjust technical level
        if "complex" in feedback.lower() or "technical" in feedback.lower():
            user_prefs["technical_level"] = "high"
        elif "simple" in feedback.lower() or "basic" in feedback.lower():
            user_prefs["technical_level"] = "low"

    def get_user_adapted_response(
        self, user_id: int, base_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt response based on user preferences"""
        if user_id not in self.user_preferences:
            return base_response

        user_prefs = self.user_preferences[user_id]
        adapted_response = base_response.copy()

        # Modify based on humor preference
        if not user_prefs["prefers_humor"] and self.humor_setting > 50:
            # Reduce humor for this user
            adapted_response["humor_level"] = min(25, self.humor_setting)

        # Modify based on technical level
        if user_prefs["technical_level"] == "high":
            adapted_response["complexity"] = "expert"
        elif user_prefs["technical_level"] == "low":
            adapted_response["complexity"] = "basic"

        return adapted_response

    def generate_tars_quote(self) -> str:
        """Generate TARS-style quotes and responses"""
        quotes = [
            "That's what I do. That's my job.",
            "It's not possible. No, it's necessary.",
            "I have a cue light I can use to show you when I'm joking, if you like.",
            "Cooper, this is no time for caution.",
            "Maybe we should ask the robot that helped kill the rest of the crew.",
            "I'm perfectly calibrated to your specifications.",
            "Analyzing humor parameters... Standby for wit.",
            "Mission efficiency: Optimal. Personality subroutines: Fully operational.",
        ]

        return random.choice(quotes)

    def get_problem_solving_approach(self, problem: str) -> Dict[str, Any]:
        """TARS-like problem solving approach"""
        return {
            "analysis": "Breaking down problem into component parameters...",
            "approach": "Systematic evaluation of all available options...",
            "confidence": f"{self.intelligence_level}% problem resolution probability",
            "recommendation": self._generate_analytical_response(problem, {}),
            "backup_plan": "Multiple contingency protocols available if needed.",
            "tars_note": self.generate_tars_quote(),
        }

    def get_current_settings_display(self) -> str:
        """Get current TARS settings display"""
        return f"""
🤖 **TARS Personality Configuration**
```
Humor Setting:     {self.humor_setting}%
Honesty Level:     {self.honesty_level}%
Loyalty Rating:    {self.loyalty_level}%
Intelligence:      {self.intelligence_level}%
Efficiency:        {self.efficiency_rating}%
Adaptability:      {self.adaptability}%
Current Mode:      {self.current_mode.value}
```
*"That's what I do. That's my job."* - TARS
        """


# Global TARS personality instance
_tars_personality = None


def get_tars_personality() -> TARSPersonalityCore:
    """Get global TARS personality instance"""
    global _tars_personality
    if _tars_personality is None:
        _tars_personality = TARSPersonalityCore()
    return _tars_personality


def initialize_tars_personality() -> TARSPersonalityCore:
    """Initialize global TARS personality"""
    global _tars_personality
    _tars_personality = TARSPersonalityCore()
    return _tars_personality
