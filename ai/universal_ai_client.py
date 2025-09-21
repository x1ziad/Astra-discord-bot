"""
Universal AI Client for Astra Bot
Provides a unified interface for multiple AI providers
"""

import asyncio
import logging
import aiohttp
import json
import os
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger("astra.universal_ai_client")


class AIProvider(Enum):
    """Supported AI providers"""

    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


@dataclass
class ConversationContext:
    """Enhanced conversation context with rich metadata"""

    user_id: int
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    message_history: List[Dict[str, Any]] = None
    user_profile: Dict[str, Any] = None
    emotional_context: Dict[str, Any] = None
    topics: List[str] = None
    conversation_stage: str = "ongoing"  # greeting, ongoing, closing
    last_interaction: Optional[datetime] = None

    def __post_init__(self):
        if self.message_history is None:
            self.message_history = []
        if self.user_profile is None:
            self.user_profile = {}
        if self.emotional_context is None:
            self.emotional_context = {}
        if self.topics is None:
            self.topics = []


@dataclass
class AIResponse:
    """Standardized AI response format"""

    content: str
    model: str
    provider: str
    usage: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    context_used: Optional[ConversationContext] = None
    confidence_score: float = 0.0

    def __str__(self):
        return self.content


class UniversalAIClient:
    """Universal AI client supporting multiple providers"""

    def __init__(self, api_key: str = None, provider: str = "openrouter", **kwargs):
        self.api_key = (
            api_key or os.getenv("AI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        )
        self.provider = AIProvider(provider) if isinstance(provider, str) else provider

        # Provider-specific configuration
        self.config = {
            AIProvider.OPENROUTER: {
                "base_url": "https://openrouter.ai/api/v1",
                "default_model": "deepseek/deepseek-r1:nitro",
                "headers": {
                    "HTTP-Referer": "https://github.com/x1ziad/Astra-discord-bot",
                    "X-Title": "Astra Discord Bot",
                },
            },
            AIProvider.OPENAI: {
                "base_url": "https://api.openai.com/v1",
                "default_model": "gpt-4",
                "headers": {},
            },
        }

        # Default parameters
        self.max_tokens = kwargs.get("max_tokens", 2000)
        self.temperature = kwargs.get("temperature", 0.7)
        self.model = kwargs.get("model", self.config[self.provider]["default_model"])

        # Enhanced context settings
        self.max_context_messages = kwargs.get(
            "max_context_messages", 8
        )  # Reduced for performance
        self.context_window_tokens = kwargs.get("context_window_tokens", 4000)
        self.enable_emotional_intelligence = kwargs.get(
            "enable_emotional_intelligence", True
        )
        self.enable_topic_tracking = kwargs.get("enable_topic_tracking", True)
        self.enable_memory_system = kwargs.get("enable_memory_system", True)

        # Memory for conversation contexts
        self.conversation_contexts: Dict[str, ConversationContext] = {}

        # Long-term memory system
        self.user_memories: Dict[int, Dict[str, Any]] = {}
        self.important_facts: Dict[str, List[Dict[str, Any]]] = {}

        # HTTP session
        self.session = None

    def is_available(self) -> bool:
        """Check if the client is properly configured"""
        return bool(self.api_key) and self.provider in self.config

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _ensure_session(self):
        """Ensure HTTP session is available"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    def _extract_important_facts(
        self, message: str, response: str, user_id: int
    ) -> List[Dict[str, Any]]:
        """Extract important facts from conversation for long-term memory"""
        facts = []
        message_lower = message.lower()

        # Personal information indicators
        personal_patterns = {
            "name": ["my name is", "i'm", "call me", "i am"],
            "location": ["i live in", "i'm from", "from", "located in"],
            "occupation": ["i work as", "my job", "i'm a", "work at"],
            "age": ["i'm", "years old", "my age"],
            "interests": ["i like", "i love", "i enjoy", "i'm into", "favorite"],
            "relationship": [
                "my",
                "girlfriend",
                "boyfriend",
                "wife",
                "husband",
                "partner",
            ],
            "achievement": ["i just", "i won", "i got", "i achieved", "i completed"],
            "problem": [
                "i'm having trouble",
                "i need help",
                "i'm struggling",
                "issue with",
            ],
            "goal": ["i want to", "i'm trying to", "my goal", "i plan to"],
        }

        current_time = datetime.now()

        for fact_type, patterns in personal_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    # Extract the relevant part of the message
                    start_idx = message_lower.find(pattern)
                    if start_idx != -1:
                        # Get the sentence containing this pattern
                        sentences = message.split(".")
                        for sentence in sentences:
                            if pattern in sentence.lower():
                                facts.append(
                                    {
                                        "type": fact_type,
                                        "content": sentence.strip(),
                                        "timestamp": current_time.isoformat(),
                                        "context": (
                                            message[:100] + "..."
                                            if len(message) > 100
                                            else message
                                        ),
                                        "confidence": (
                                            0.8
                                            if fact_type in ["name", "location"]
                                            else 0.6
                                        ),
                                    }
                                )
                                break

        # Extract mentioned preferences and dislikes
        if "hate" in message_lower or "don't like" in message_lower:
            facts.append(
                {
                    "type": "dislike",
                    "content": message,
                    "timestamp": current_time.isoformat(),
                    "confidence": 0.7,
                }
            )

        return facts

    def _update_user_memory(self, user_id: int, facts: List[Dict[str, Any]]):
        """Update long-term memory for a user"""
        if not self.enable_memory_system:
            return

        if user_id not in self.user_memories:
            self.user_memories[user_id] = {
                "facts": [],
                "preferences": {},
                "important_dates": [],
                "communication_patterns": {},
                "last_updated": datetime.now().isoformat(),
            }

        user_memory = self.user_memories[user_id]

        for fact in facts:
            # Avoid duplicates
            existing_facts = [f["content"] for f in user_memory["facts"]]
            if fact["content"] not in existing_facts:
                user_memory["facts"].append(fact)

        # Keep only recent and high-confidence facts
        user_memory["facts"] = sorted(
            user_memory["facts"],
            key=lambda x: (x["confidence"], x["timestamp"]),
            reverse=True,
        )[
            :50
        ]  # Keep top 50 facts

        user_memory["last_updated"] = datetime.now().isoformat()

    def _get_relevant_memories(
        self, user_id: int, current_message: str
    ) -> List[Dict[str, Any]]:
        """Get relevant memories for the current conversation"""
        if not self.enable_memory_system or user_id not in self.user_memories:
            return []

        user_memory = self.user_memories[user_id]
        relevant_facts = []

        # Get recent high-confidence facts
        for fact in user_memory["facts"][:10]:  # Top 10 facts
            if fact["confidence"] > 0.6:
                relevant_facts.append(fact)

        # Find contextually relevant facts
        message_words = set(current_message.lower().split())
        for fact in user_memory["facts"]:
            fact_words = set(fact["content"].lower().split())
            if len(message_words.intersection(fact_words)) > 1:  # Shared words
                if fact not in relevant_facts:
                    relevant_facts.append(fact)

        return relevant_facts[:5]  # Return top 5 relevant facts

    def _get_context_key(
        self,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ) -> str:
        """Generate a unique key for conversation context"""
        if guild_id and channel_id:
            return f"{guild_id}:{channel_id}:{user_id}"
        elif guild_id:
            return f"{guild_id}:{user_id}"
        else:
            return f"dm:{user_id}"

    def _get_or_create_context(
        self,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ) -> ConversationContext:
        """Get or create conversation context for a user"""
        context_key = self._get_context_key(user_id, guild_id, channel_id)

        if context_key not in self.conversation_contexts:
            self.conversation_contexts[context_key] = ConversationContext(
                user_id=user_id,
                guild_id=guild_id,
                channel_id=channel_id,
                last_interaction=datetime.now(),
            )

        return self.conversation_contexts[context_key]

    async def load_conversation_context_from_db(
        self,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        db_connection=None,
    ) -> Optional[ConversationContext]:
        """Load conversation context from database storage"""
        try:
            if not db_connection:
                # Try to import the database connection if available
                try:
                    from utils.database import db

                    db_connection = db
                except ImportError:
                    logger.warning(
                        "Database connection not available for context loading"
                    )
                    return None

            # Load from database using the same key format as the main bot
            context_db_key = (
                f"message_context_{guild_id if guild_id else 'dm'}_{channel_id}"
            )
            db_context = await db_connection.get(
                "conversation_contexts", context_db_key, {}
            )

            if not db_context or not db_context.get("messages"):
                return None

            # Convert database context to ConversationContext
            recent_messages = db_context.get("messages", [])[-20:]  # Last 20 messages

            # Build message history in the format expected by AI
            message_history = []
            for msg in recent_messages:
                role = "assistant" if msg.get("user_id") == "bot" else "user"
                message_history.append(
                    {
                        "role": role,
                        "content": msg.get("content", ""),
                        "timestamp": msg.get("timestamp", ""),
                    }
                )

            # Create conversation context
            context = ConversationContext(
                user_id=user_id,
                guild_id=guild_id,
                channel_id=channel_id,
                message_history=message_history,
                last_interaction=datetime.fromisoformat(
                    db_context.get("last_activity", datetime.now().isoformat())
                ),
            )

            # Extract topics from recent messages
            if self.enable_topic_tracking:
                all_content = " ".join(
                    [msg.get("content", "") for msg in recent_messages]
                )
                context.topics = self._extract_topics(all_content)

            # Store in memory cache
            context_key = self._get_context_key(user_id, guild_id, channel_id)
            self.conversation_contexts[context_key] = context

            return context

        except Exception as e:
            logger.error(f"Error loading conversation context from database: {e}")
            return None

    async def save_conversation_context_to_db(
        self, context: ConversationContext, db_connection=None
    ):
        """Save conversation context to database storage"""
        try:
            if not db_connection:
                try:
                    from utils.database import db

                    db_connection = db
                except ImportError:
                    logger.warning(
                        "Database connection not available for context saving"
                    )
                    return

            # Convert ConversationContext to database format
            context_db_key = f"message_context_{context.guild_id if context.guild_id else 'dm'}_{context.channel_id}"

            # Get existing context or create new
            existing_context = await db_connection.get(
                "conversation_contexts", context_db_key, {"messages": []}
            )

            # Add recent interactions to database format
            for msg in context.message_history[-5:]:  # Last 5 messages for performance
                db_message = {
                    "user_id": context.user_id if msg.get("role") == "user" else "bot",
                    "username": "Bot" if msg.get("role") == "assistant" else "User",
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                    "channel_id": context.channel_id,
                    "guild_id": context.guild_id,
                }

                # Check if message already exists (avoid duplicates)
                if not any(
                    existing_msg.get("content") == db_message["content"]
                    and existing_msg.get("timestamp") == db_message["timestamp"]
                    for existing_msg in existing_context["messages"]
                ):
                    existing_context["messages"].append(db_message)

            # Update metadata
            existing_context.update(
                {
                    "last_activity": (
                        context.last_interaction.isoformat()
                        if context.last_interaction
                        else datetime.now().isoformat()
                    ),
                    "channel_id": context.channel_id,
                    "guild_id": context.guild_id,
                    "topics": context.topics if context.topics else [],
                    "conversation_stage": context.conversation_stage,
                }
            )

            # Keep only recent messages
            if len(existing_context["messages"]) > 50:
                existing_context["messages"] = existing_context["messages"][-50:]

            # Save to database
            await db_connection.set(
                "conversation_contexts", context_db_key, existing_context
            )

        except Exception as e:
            logger.error(f"Error saving conversation context to database: {e}")

    def _analyze_emotional_context(self, message: str) -> Dict[str, Any]:
        """Advanced emotional context analysis with sentiment and intensity detection"""
        emotional_indicators = {
            "excited": {
                "keywords": [
                    "!",
                    "wow",
                    "amazing",
                    "awesome",
                    "excited",
                    "can't wait",
                    "yay",
                    "woohoo",
                    "fantastic",
                    "incredible",
                ],
                "patterns": ["!!!+", "WOW", "AMAZING", "SO GOOD", "LOVE IT"],
                "weight": 1.2,
            },
            "happy": {
                "keywords": [
                    "happy",
                    "glad",
                    "pleased",
                    "good",
                    "great",
                    "wonderful",
                    "nice",
                    "perfect",
                    "excellent",
                    "brilliant",
                ],
                "patterns": [":)", ":D", "😊", "😄", "🙂", "❤️", "💖"],
                "weight": 1.0,
            },
            "sad": {
                "keywords": [
                    "sad",
                    "down",
                    "depressed",
                    "unhappy",
                    "disappointed",
                    "upset",
                    "crying",
                    "tears",
                    "heartbroken",
                ],
                "patterns": [":(", "😢", "😭", "💔", "😞"],
                "weight": 1.3,
            },
            "angry": {
                "keywords": [
                    "angry",
                    "mad",
                    "frustrated",
                    "annoyed",
                    "upset",
                    "furious",
                    "pissed",
                    "irritated",
                    "rage",
                ],
                "patterns": [">:(", "😡", "😠", "🤬"],
                "weight": 1.5,
            },
            "confused": {
                "keywords": [
                    "confused",
                    "don't understand",
                    "unclear",
                    "help",
                    "lost",
                    "puzzled",
                    "what",
                    "how",
                    "why",
                ],
                "patterns": ["???", "??", "🤔", "😕"],
                "weight": 0.8,
            },
            "anxious": {
                "keywords": [
                    "worried",
                    "nervous",
                    "anxious",
                    "stressed",
                    "concerned",
                    "afraid",
                    "scared",
                    "panic",
                ],
                "patterns": ["😰", "😨", "😟", "😖"],
                "weight": 1.4,
            },
            "grateful": {
                "keywords": [
                    "thanks",
                    "thank you",
                    "grateful",
                    "appreciate",
                    "thankful",
                    "blessed",
                ],
                "patterns": ["🙏", "😊", "❤️"],
                "weight": 1.1,
            },
            "frustrated": {
                "keywords": [
                    "ugh",
                    "argh",
                    "sigh",
                    "frustrated",
                    "tired",
                    "exhausted",
                    "done",
                    "fed up",
                ],
                "patterns": ["😤", "😑", "🙄"],
                "weight": 1.2,
            },
        }

        message_lower = message.lower()
        detected_emotions = {}

        # Analyze keywords and patterns
        for emotion, data in emotional_indicators.items():
            score = 0

            # Check keywords
            for keyword in data["keywords"]:
                if keyword in message_lower:
                    score += 1

            # Check patterns (emojis, punctuation)
            for pattern in data["patterns"]:
                if pattern.lower() in message_lower:
                    score += 1.5  # Patterns have higher weight

            # Apply emotion weight
            if score > 0:
                detected_emotions[emotion] = score * data["weight"]

        # Determine dominant emotion and intensity
        dominant_emotion = "neutral"
        emotional_intensity = 0.0

        if detected_emotions:
            dominant_emotion = max(detected_emotions, key=detected_emotions.get)
            # Calculate intensity based on total emotional indicators
            total_score = sum(detected_emotions.values())
            emotional_intensity = min(total_score * 0.2, 1.0)

        # Additional context analysis
        message_length = len(message.split())
        caps_ratio = sum(1 for c in message if c.isupper()) / max(len(message), 1)

        # Adjust intensity based on message characteristics
        if caps_ratio > 0.3:  # Lots of caps = higher intensity
            emotional_intensity = min(emotional_intensity * 1.3, 1.0)

        if message_length > 50:  # Long messages often indicate higher investment
            emotional_intensity = min(emotional_intensity * 1.1, 1.0)

        # Detect conversation stage indicators
        conversation_stage = "ongoing"
        greeting_words = [
            "hello",
            "hi",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
            "greetings",
        ]
        farewell_words = [
            "goodbye",
            "bye",
            "see you",
            "talk later",
            "gotta go",
            "farewell",
        ]

        if any(word in message_lower for word in greeting_words):
            conversation_stage = "greeting"
        elif any(word in message_lower for word in farewell_words):
            conversation_stage = "farewell"

        return {
            "dominant_emotion": dominant_emotion,
            "emotions_detected": detected_emotions,
            "emotional_intensity": emotional_intensity,
            "conversation_stage": conversation_stage,
            "caps_ratio": caps_ratio,
            "message_length_category": (
                "long"
                if message_length > 30
                else "medium" if message_length > 10 else "short"
            ),
            "urgency_indicators": self._detect_urgency(message_lower),
        }

    def _detect_urgency(self, message_lower: str) -> Dict[str, Any]:
        """Detect urgency and response expectation indicators"""
        urgent_keywords = [
            "urgent",
            "asap",
            "quickly",
            "fast",
            "emergency",
            "help",
            "now",
            "immediately",
        ]
        question_patterns = [
            "?",
            "how",
            "what",
            "when",
            "where",
            "why",
            "can you",
            "could you",
            "would you",
        ]

        urgency_score = sum(
            1 for keyword in urgent_keywords if keyword in message_lower
        )
        has_questions = any(pattern in message_lower for pattern in question_patterns)

        return {
            "urgency_score": min(urgency_score * 0.3, 1.0),
            "has_questions": has_questions,
            "expects_quick_response": urgency_score > 0 or has_questions,
        }

    def _extract_topics(self, message: str) -> List[str]:
        """Extract potential topics from a message"""
        # Simple topic extraction - could be enhanced with NLP
        words = message.lower().split()

        # Common topic indicators
        topic_keywords = {
            "gaming": ["game", "play", "gaming", "steam", "xbox", "playstation"],
            "programming": [
                "code",
                "python",
                "javascript",
                "programming",
                "coding",
                "bug",
            ],
            "music": ["music", "song", "album", "artist", "spotify", "listen"],
            "movies": ["movie", "film", "watch", "cinema", "netflix", "series"],
            "food": ["food", "eat", "cooking", "recipe", "restaurant", "meal"],
            "work": ["work", "job", "office", "meeting", "project", "deadline"],
            "school": ["school", "class", "homework", "exam", "study", "university"],
            "weather": ["weather", "rain", "sunny", "cold", "hot", "temperature"],
            "sports": ["sport", "football", "basketball", "soccer", "game", "team"],
            "technology": ["tech", "computer", "phone", "software", "hardware", "ai"],
        }

        detected_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in words for keyword in keywords):
                detected_topics.append(topic)

        return detected_topics

    def _build_enhanced_context_messages(
        self, context: ConversationContext, current_message: str
    ) -> List[Dict[str, str]]:
        """Build enhanced context messages with conversation history and analysis"""
        messages = []

        # Add system message with rich context
        system_prompt = self._build_enhanced_system_prompt(context, current_message)
        messages.append({"role": "system", "content": system_prompt})

        # Add recent conversation history (sliding window)
        recent_messages = context.message_history[-self.max_context_messages :]
        for msg in recent_messages:
            messages.append(
                {"role": msg.get("role", "user"), "content": msg.get("content", "")}
            )

        return messages

    def _build_enhanced_system_prompt(
        self, context: ConversationContext, current_message: str
    ) -> str:
        """Build a system prompt - concise or detailed based on config"""
        from config.unified_config import unified_config

        # Check if concise prompts are enabled (default: True for performance)
        use_concise = unified_config.get_setting("use_concise_prompts", True)

        if use_concise:
            return self._build_concise_prompt(context, current_message)
        else:
            return self._build_detailed_prompt(context, current_message)

    def _build_concise_prompt(
        self, context: ConversationContext, current_message: str
    ) -> str:
        """Build a concise system prompt for faster responses"""
        base_prompt = "You are Astra, a helpful AI assistant for Discord. Be natural, engaging, and context-aware."

        prompt_parts = [base_prompt]

        # Add key user context only
        if context.user_profile:
            name = context.user_profile.get("name", "")
            if name:
                prompt_parts.append(f"User: {name}")

            # Simplified relationship level
            count = context.user_profile.get("interaction_count", 0)
            if count > 10:
                prompt_parts.append("Familiar user - be friendly")
            elif count > 3:
                prompt_parts.append("Getting to know them")

        # Essential emotional context only
        if context.emotional_context:
            emotion = context.emotional_context.get("dominant_emotion", "neutral")
            if emotion in ["sad", "angry", "anxious"]:
                prompt_parts.append(f"User seems {emotion} - be supportive")
            elif emotion in ["excited", "happy"]:
                prompt_parts.append(f"User is {emotion} - match their energy")

        # Recent topics (max 2)
        if context.topics:
            recent = context.topics[-2:]
            if recent:
                prompt_parts.append(f"Topics: {', '.join(recent)}")

        # Simple guidelines
        prompt_parts.append("Be helpful, natural, and conversational.")

        return " | ".join(prompt_parts)

    def _build_detailed_prompt(
        self, context: ConversationContext, current_message: str
    ) -> str:
        """Build a detailed system prompt (original version for when detail is needed)"""
        prompt_parts = [
            "You are Astra, an advanced AI assistant for a Discord community. You are helpful, engaging, and highly context-aware.",
            "You possess emotional intelligence and adapt your responses based on the user's emotional state, conversation history, and communication patterns.",
        ]

        # Add memory-based user context
        if context.user_id and self.enable_memory_system:
            relevant_memories = self._get_relevant_memories(
                context.user_id, current_message
            )
            if relevant_memories:
                prompt_parts.append("\nWhat you remember about this user:")
                for memory in relevant_memories[:2]:  # Top 2 most relevant
                    if memory["type"] in ["name", "occupation", "interests"]:
                        prompt_parts.append(f"- {memory['content']}")

        # Add user context
        if context.user_profile:
            name = context.user_profile.get("name", "")
            if name:
                prompt_parts.append(f"You're talking with {name}.")

            interaction_count = context.user_profile.get("interaction_count", 0)
            if interaction_count > 20:
                prompt_parts.append(
                    "You have a well-established relationship with this user."
                )
            elif interaction_count > 10:
                prompt_parts.append(
                    "You're developing a good relationship with this user."
                )
            elif interaction_count > 3:
                prompt_parts.append("You're getting to know this user better.")

        # Add emotional context
        if context.emotional_context:
            emotion = context.emotional_context.get("dominant_emotion", "neutral")
            if emotion != "neutral":
                emotion_guidance = {
                    "excited": "The user is excited! Match their enthusiasm.",
                    "happy": "The user is in a good mood. Be positive.",
                    "sad": "The user seems sad. Be empathetic and supportive.",
                    "angry": "The user appears frustrated. Be understanding and calm.",
                    "anxious": "The user seems worried. Be reassuring.",
                }
                if emotion in emotion_guidance:
                    prompt_parts.append(emotion_guidance[emotion])

        # Add topics
        if context.topics:
            recent_topics = context.topics[-2:]
            topics_str = ", ".join(recent_topics)
            prompt_parts.append(f"Recent topics: {topics_str}")

        # Add guidelines
        prompt_parts.append("Respond naturally and be helpful.")

        return "\n".join(prompt_parts)

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for the current provider"""
        base_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        provider_headers = self.config[self.provider]["headers"]
        base_headers.update(provider_headers)

        return base_headers

    def _build_payload(
        self, message: str, context: Optional[List[Dict[str, str]]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Build request payload for the current provider"""

        # Build messages
        messages = []
        if context:
            messages.extend(context)

        messages.append({"role": "user", "content": message})

        # Base payload
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": False,
        }

        return payload

    async def generate_response(
        self,
        message: str,
        context: Optional[List[Dict[str, str]]] = None,
        user_id: Optional[int] = None,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate enhanced AI response with deep context understanding"""

        await self._ensure_session()

        if not self.is_available():
            raise ValueError(
                f"AI client not properly configured for {self.provider.value}"
            )

        # Get or create conversation context if user info provided
        conversation_context = None
        if user_id is not None:
            # First try to load from database for full conversation history
            conversation_context = await self.load_conversation_context_from_db(
                user_id, guild_id, channel_id
            )

            # If no database context, create new one
            if not conversation_context:
                conversation_context = self._get_or_create_context(
                    user_id, guild_id, channel_id
                )

            # Update user profile if provided
            if user_profile:
                conversation_context.user_profile.update(user_profile)

            # Analyze current message for emotional context and topics
            if self.enable_emotional_intelligence:
                emotional_analysis = self._analyze_emotional_context(message)
                conversation_context.emotional_context = emotional_analysis

            if self.enable_topic_tracking:
                topics = self._extract_topics(message)
                if topics:
                    # Add new topics and keep recent ones
                    conversation_context.topics.extend(topics)
                    conversation_context.topics = list(
                        set(conversation_context.topics[-10:])
                    )  # Keep last 10 unique topics

            # Update conversation stage
            greeting_indicators = ["hello", "hi", "hey", "good morning", "good evening"]
            if (
                any(indicator in message.lower() for indicator in greeting_indicators)
                and not conversation_context.message_history
            ):
                conversation_context.conversation_stage = "greeting"
            else:
                conversation_context.conversation_stage = "ongoing"

            # Add current message to history
            conversation_context.message_history.append(
                {
                    "role": "user",
                    "content": message,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Trim history if too long
            if (
                len(conversation_context.message_history)
                > self.max_context_messages * 2
            ):
                conversation_context.message_history = (
                    conversation_context.message_history[-self.max_context_messages :]
                )

            conversation_context.last_interaction = datetime.now()

        # Build messages with enhanced context
        if conversation_context:
            messages = self._build_enhanced_context_messages(
                conversation_context, message
            )
        elif context:
            # Fallback to provided context
            messages = list(context)
            messages.append({"role": "user", "content": message})
        else:
            # Basic message structure
            messages = [
                {
                    "role": "system",
                    "content": "You are Astra, a helpful and engaging AI assistant. Respond naturally and appropriately to the user's message.",
                },
                {"role": "user", "content": message},
            ]

        provider_config = self.config[self.provider]
        url = f"{provider_config['base_url']}/chat/completions"

        # Build payload
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": False,
        }

        headers = self._get_headers()

        try:
            async with self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:

                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"{self.provider.value} API error {response.status}: {error_text}"
                    )
                    raise Exception(
                        f"{self.provider.value} API error: {response.status} - {error_text}"
                    )

                result = await response.json()

                # Extract response content
                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})

                # Add response to conversation history
                if conversation_context:
                    conversation_context.message_history.append(
                        {
                            "role": "assistant",
                            "content": content,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                    # Extract and store important facts for memory system
                    if self.enable_memory_system and user_id is not None:
                        important_facts = self._extract_important_facts(
                            message, content, user_id
                        )
                        if important_facts:
                            self._update_user_memory(user_id, important_facts)

                # Calculate confidence score based on context richness
                confidence_score = self._calculate_confidence_score(
                    conversation_context, usage
                )

                # Save updated conversation context to database
                if conversation_context:
                    try:
                        await self.save_conversation_context_to_db(conversation_context)
                    except Exception as e:
                        logger.warning(
                            f"Failed to save conversation context to database: {e}"
                        )

                return AIResponse(
                    content=content,
                    model=payload["model"],
                    provider=self.provider.value,
                    usage=usage,
                    metadata={
                        "response_id": result.get("id"),
                        "finish_reason": result["choices"][0].get("finish_reason"),
                        "created": result.get("created"),
                        "context_messages_used": len(messages),
                        "emotional_context": (
                            conversation_context.emotional_context
                            if conversation_context
                            else None
                        ),
                        "topics": (
                            conversation_context.topics
                            if conversation_context
                            else None
                        ),
                    },
                    created_at=datetime.now(),
                    context_used=conversation_context,
                    confidence_score=confidence_score,
                )

        except asyncio.TimeoutError:
            logger.error(f"{self.provider.value} API request timed out")
            raise Exception(f"{self.provider.value} API request timed out")
        except Exception as e:
            logger.error(f"{self.provider.value} API error: {e}")
            raise

    def _calculate_confidence_score(
        self, context: Optional[ConversationContext], usage: Dict[str, Any]
    ) -> float:
        """Calculate confidence score based on available context and response quality"""
        score = 0.5  # Base score

        if context:
            # More history = higher confidence
            if len(context.message_history) > 5:
                score += 0.2
            elif len(context.message_history) > 2:
                score += 0.1

            # User profile information
            if context.user_profile:
                score += 0.1

            # Emotional context understanding
            if context.emotional_context.get("dominant_emotion") != "neutral":
                score += 0.1

            # Topic relevance
            if context.topics:
                score += 0.1

        # Response quality indicators from usage
        if usage.get("total_tokens", 0) > 100:  # Substantial response
            score += 0.1

        return min(score, 1.0)

    async def clear_context(
        self,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ):
        """Clear conversation context for a user"""
        context_key = self._get_context_key(user_id, guild_id, channel_id)
        if context_key in self.conversation_contexts:
            del self.conversation_contexts[context_key]

    async def get_context_summary(
        self,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get a summary of the conversation context"""
        context_key = self._get_context_key(user_id, guild_id, channel_id)
        if context_key not in self.conversation_contexts:
            return {"status": "no_context"}

        context = self.conversation_contexts[context_key]
        return {
            "message_count": len(context.message_history),
            "topics": context.topics,
            "dominant_emotion": context.emotional_context.get(
                "dominant_emotion", "neutral"
            ),
            "conversation_stage": context.conversation_stage,
            "last_interaction": (
                context.last_interaction.isoformat()
                if context.last_interaction
                else None
            ),
            "user_profile_keys": list(context.user_profile.keys()),
        }

    async def update_user_profile(
        self,
        user_id: int,
        profile_data: Dict[str, Any],
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ):
        """Update user profile information"""
        context = self._get_or_create_context(user_id, guild_id, channel_id)
        context.user_profile.update(profile_data)

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available models for the current provider"""

        await self._ensure_session()

        if not self.is_available():
            return []

        provider_config = self.config[self.provider]
        url = f"{provider_config['base_url']}/models"
        headers = self._get_headers()

        try:
            async with self.session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:

                if response.status == 200:
                    result = await response.json()
                    return result.get("data", [])
                else:
                    logger.warning(
                        f"Failed to fetch {self.provider.value} models: {response.status}"
                    )
                    return []

        except Exception as e:
            logger.error(f"Error fetching {self.provider.value} models: {e}")
            return []

    async def test_connection(self) -> bool:
        """Test connection to the AI provider"""

        if not self.is_available():
            return False

        try:
            response = await self.generate_response(
                "Hello! This is a test message. Please respond with 'Test successful!'",
                max_tokens=50,
            )
            return bool(response.content)
        except Exception as e:
            logger.error(f"{self.provider.value} connection test failed: {e}")
            return False

    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None


# Factory function for creating clients
async def create_ai_client(
    provider: str = "openrouter", api_key: str = None, **kwargs
) -> UniversalAIClient:
    """Create and initialize an AI client"""
    client = UniversalAIClient(api_key=api_key, provider=provider, **kwargs)
    await client._ensure_session()
    return client


# Convenience functions for specific providers
async def create_openrouter_client(api_key: str = None, **kwargs) -> UniversalAIClient:
    """Create OpenRouter client"""
    return await create_ai_client("openrouter", api_key, **kwargs)


async def create_openai_client(api_key: str = None, **kwargs) -> UniversalAIClient:
    """Create OpenAI client"""
    return await create_ai_client("openai", api_key, **kwargs)


if __name__ == "__main__":
    # Test the Universal AI client
    async def test():
        client = UniversalAIClient()
        if client.is_available():
            print(f"Universal AI client configured for {client.provider.value}")
            try:
                response = await client.generate_response("Hello, how are you?")
                print(f"Response: {response.content}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Universal AI client not configured")

        await client.close()

    asyncio.run(test())
