#!/usr/bin/env python3
"""
Enhanced Response Generator - More Concise and Contextual
Provides intelligent response enhancement and creator mention detection
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("astra.response_enhancer")


class ResponseEnhancer:
    """Enhances AI responses with contextual intelligence and creator mention logic"""

    def __init__(self):
        self.creator_patterns = [
            r"\b(who\s+(made|created|built|designed|developed)\s+you)\b",
            r"\b(your\s+(creator|maker|developer|author|owner))\b",
            r"\b(who\s+is\s+your\s+(creator|maker|developer))\b",
            r"\b(who\s+do\s+you\s+belong\s+to)\b",
            r"\b(who\s+owns\s+you)\b",
            r"\b(who\s+(programmed|coded)\s+you)\b",
        ]

        # Compile patterns for efficiency
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.creator_patterns
        ]

    def should_mention_creator(
        self, message_content: str, context: Dict[str, Any]
    ) -> bool:
        """Determine if creator should be mentioned based on message content and context"""

        # Check for direct creator-related questions
        for pattern in self.compiled_patterns:
            if pattern.search(message_content):
                return True

        # Check for origin/source questions
        origin_keywords = [
            "origin",
            "source",
            "where did you come from",
            "how were you made",
        ]
        message_lower = message_content.lower()

        if any(keyword in message_lower for keyword in origin_keywords):
            return True

        # Context-based decisions
        conversation_history = context.get("conversation_history", [])

        # If creator was mentioned in recent context, continue that thread
        recent_messages = " ".join(conversation_history[-3:]).lower()
        if "creator" in recent_messages or "made you" in recent_messages:
            return True

        return False

    def get_contextual_response_style(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Determine appropriate response style based on context"""

        style = {"length": "medium", "tone": "balanced", "formality": "casual"}

        # Analyze context for style cues
        message = context.get("message_content", "").lower()
        user_mood = context.get("user_mood", "neutral")
        channel_name = context.get("channel", "")

        # Length adjustments
        if "?" in message or any(
            word in message for word in ["how", "what", "why", "explain"]
        ):
            style["length"] = "long"  # Questions need thorough answers
        elif any(word in message for word in ["thanks", "ty", "ok", "cool"]):
            style["length"] = "short"  # Simple acknowledgments

        # Tone adjustments
        if user_mood in ["stressed", "sad", "angry"]:
            style["tone"] = "supportive"
        elif user_mood in ["excited", "happy"]:
            style["tone"] = "enthusiastic"
        elif "serious" in message or "important" in message:
            style["tone"] = "professional"

        # Formality adjustments
        if "admin" in channel_name.lower() or "mod" in channel_name.lower():
            style["formality"] = "professional"
        elif "casual" in channel_name.lower() or "chat" in channel_name.lower():
            style["formality"] = "casual"

        return style

    def enhance_response_guidelines(
        self,
        message_content: str,
        context: Dict[str, Any],
        style_preferences: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generate enhanced response guidelines based on message content and context"""

        guidelines = {
            "max_words": 120,
            "tone": "balanced",
            "style": "conversational",
            "specific_instructions": [],
            "mention_creator": False,
        }

        # Apply style preferences if provided (from personality system)
        if style_preferences:
            guidelines.update(style_preferences)

        # Context-aware adjustments
        message_lower = message_content.lower()

        # Adjust for question vs statement
        if any(
            word in message_lower
            for word in ["?", "how", "what", "why", "when", "where"]
        ):
            guidelines["style"] = "informative"
            guidelines["specific_instructions"].append(
                "Provide helpful and accurate information"
            )
            # Don't override personality-set word limits unless necessary
            if style_preferences is None or "max_words" not in style_preferences:
                guidelines["max_words"] = 150

        # Adjust for emotional content
        if any(
            word in message_lower
            for word in ["sad", "upset", "worried", "stressed", "angry"]
        ):
            guidelines["tone"] = "supportive"
            guidelines["specific_instructions"].append(
                "Be empathetic and supportive - increase warmth"
            )
            # Shorter responses for emotional support
            if style_preferences is None or "max_words" not in style_preferences:
                guidelines["max_words"] = 100

        # Adjust for celebration/positive content
        if any(
            word in message_lower
            for word in ["awesome", "great", "amazing", "thanks", "good job"]
        ):
            guidelines["tone"] = "enthusiastic"
            guidelines["specific_instructions"].append(
                "Match the positive energy and celebrate with them"
            )
            if style_preferences is None or "max_words" not in style_preferences:
                guidelines["max_words"] = 80

        # Adjust for technical content
        if any(
            word in message_lower
            for word in ["error", "bug", "fix", "problem", "issue", "code"]
        ):
            guidelines["style"] = "technical"
            guidelines["specific_instructions"].append(
                "Be precise, solution-oriented, and technical"
            )
            # Technical responses can be longer for explanations
            if style_preferences is None or "max_words" not in style_preferences:
                guidelines["max_words"] = 200

        # Adjust for commands or direct requests
        if message_lower.startswith("astra") or "/astra" in message_lower:
            guidelines["specific_instructions"].append(
                "This is a direct command - be responsive and action-oriented"
            )

        # Check for creator mention context
        if self.should_mention_creator(message_content, context):
            guidelines["mention_creator"] = True

        # Add personality-aware instructions
        guidelines["specific_instructions"].append(
            "Respond authentically as Astra with your current personality settings"
        )
        guidelines["specific_instructions"].append(
            "You're the crew's AI companion - be confident and capable"
        )

        return guidelines
