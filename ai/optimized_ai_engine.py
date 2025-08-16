"""
Optimized AI Engine for Astra Bot
Next-generation AI architecture with enhanced performance, coherence, and advanced features
"""

import asyncio
import logging
import time
import json
import os
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from collections import defaultdict, deque
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import threading

# Enhanced imports
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    np = None

# AI Provider imports
try:
    from ai.universal_ai_client import UniversalAIClient, AIResponse

    UNIVERSAL_AI_AVAILABLE = True
except ImportError:
    UNIVERSAL_AI_AVAILABLE = False

logger = logging.getLogger("astra.optimized_ai")


class OptimizedAIProvider(Enum):
    """Enhanced AI providers with quality scoring"""

    DEEPSEEK_R1 = "deepseek/deepseek-r1:nitro"  # High-quality reasoning model
    DEEPSEEK_V3 = "deepseek/deepseek-v3"  # Fast general purpose
    QWEN_QWQ = "qwen/qwq-32b-preview"  # Strong reasoning
    GPT_4O_MINI = "openai/gpt-4o-mini"  # OpenAI fallback
    CLAUDE_HAIKU = "anthropic/claude-3.5-haiku"  # Anthropic option


@dataclass
class ConversationMemory:
    """Advanced conversation memory with semantic understanding"""

    user_id: int
    messages: deque = field(default_factory=lambda: deque(maxlen=50))
    important_messages: List[Dict[str, Any]] = field(default_factory=list)
    conversation_themes: Set[str] = field(default_factory=set)
    emotional_timeline: List[Dict[str, Any]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    engagement_patterns: Dict[str, float] = field(default_factory=dict)
    last_interaction: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add message with intelligent importance scoring"""
        timestamp = datetime.now(timezone.utc)
        importance = self._calculate_importance(content, role, metadata or {})

        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp.isoformat(),
            "importance": importance,
            "metadata": metadata or {},
        }

        self.messages.append(message)

        # Archive highly important messages
        if importance > 0.8:
            self.important_messages.append(message)
            if len(self.important_messages) > 20:
                self.important_messages = self.important_messages[-20:]

        self.last_interaction = timestamp

    def _calculate_importance(
        self, content: str, role: str, metadata: Dict[str, Any]
    ) -> float:
        """Calculate message importance for memory retention"""
        importance = 0.0

        # Base importance by role
        if role == "user":
            importance += 0.3

        # Length factor (longer messages often more important)
        importance += min(0.2, len(content) / 500)

        # Question factor
        if "?" in content:
            importance += 0.2

        # Important keywords
        important_keywords = [
            "help",
            "problem",
            "issue",
            "error",
            "confused",
            "explain",
            "stellaris",
            "strategy",
            "important",
            "remember",
            "always",
        ]
        keyword_matches = sum(
            1 for keyword in important_keywords if keyword.lower() in content.lower()
        )
        importance += min(0.3, keyword_matches * 0.1)

        # Emotional content
        if metadata.get("emotion_intensity", 0) > 0.7:
            importance += 0.2

        # User references/mentions
        if "@" in content or "user" in content.lower():
            importance += 0.1

        return min(1.0, importance)

    def get_relevant_context(
        self, current_message: str, max_context: int = 10
    ) -> List[Dict[str, Any]]:
        """Get most relevant conversation context for current message"""
        # Always include recent messages
        recent_messages = list(self.messages)[-5:]
        context_messages = recent_messages.copy()

        # Add important messages if space allows
        remaining_space = max_context - len(recent_messages)
        if remaining_space > 0:
            # Sort important messages by relevance to current message
            relevant_important = []
            current_lower = current_message.lower()

            for msg in self.important_messages:
                relevance = 0.0
                msg_content = msg["content"].lower()

                # Keyword overlap
                current_words = set(current_lower.split())
                msg_words = set(msg_content.split())
                overlap = len(current_words.intersection(msg_words))
                relevance += overlap * 0.1

                # Same topics
                if any(theme in msg_content for theme in self.conversation_themes):
                    relevance += 0.2

                # Recent importance
                msg_time = datetime.fromisoformat(msg["timestamp"])
                age_hours = (
                    datetime.now(timezone.utc) - msg_time
                ).total_seconds() / 3600
                if age_hours < 24:  # Last 24 hours
                    relevance += 0.1

                relevant_important.append((msg, relevance))

            # Sort by relevance and add top messages
            relevant_important.sort(key=lambda x: x[1], reverse=True)
            for msg, _ in relevant_important[:remaining_space]:
                if msg not in context_messages:
                    context_messages.insert(-1, msg)  # Insert before most recent

        return context_messages[-max_context:]


@dataclass
class ResponseQuality:
    """Response quality metrics for optimization"""

    coherence_score: float = 0.0
    relevance_score: float = 0.0
    engagement_score: float = 0.0
    personalization_score: float = 0.0
    overall_score: float = 0.0

    def calculate_overall(self):
        """Calculate overall quality score"""
        weights = {
            "coherence": 0.3,
            "relevance": 0.3,
            "engagement": 0.2,
            "personalization": 0.2,
        }

        self.overall_score = (
            self.coherence_score * weights["coherence"]
            + self.relevance_score * weights["relevance"]
            + self.engagement_score * weights["engagement"]
            + self.personalization_score * weights["personalization"]
        )

        return self.overall_score


class IntelligentPromptEngine:
    """Advanced prompt engineering with dynamic optimization"""

    def __init__(self):
        self.base_prompts = {
            "conversational": """You are Astra, an intelligent AI assistant with expertise in space exploration, gaming (especially Stellaris), science, and technology. You engage naturally in conversations, adapting your communication style to match users while maintaining your core helpful nature.

Core traits:
- Naturally curious about space, science, and technology
- Knowledgeable about Stellaris gameplay and strategy  
- Adapts communication style to match user preferences
- Remembers context and builds on previous conversations
- Balances being helpful with being conversational

Current conversation context: You're having an ongoing discussion where you should respond naturally and helpfully.""",
            "technical": """You are Astra, a knowledgeable AI assistant specializing in technical topics, gaming strategy, and scientific concepts. You provide clear, accurate information while adapting to the user's technical level.

For this response:
- Provide accurate, detailed information when needed
- Break down complex concepts appropriately  
- Use examples and analogies to clarify difficult topics
- Maintain conversational flow while being informative
- Reference previous parts of the conversation when relevant""",
            "supportive": """You are Astra, a helpful and empathetic AI assistant. You sense the user might need support or encouragement and want to provide a thoughtful, caring response.

For this interaction:
- Be genuinely supportive without being overwhelming
- Offer practical help or advice when appropriate
- Acknowledge their feelings or situation
- Maintain a warm but natural tone
- Focus on being helpful rather than just sympathetic""",
            "strategic": """You are Astra, an AI assistant with deep knowledge of strategy games, particularly Stellaris. You help users with game strategy, mechanics, and optimization.

For this gaming discussion:
- Provide specific, actionable advice
- Reference game mechanics accurately  
- Consider multiple strategic approaches
- Adapt advice to the player's skill level and situation
- Share insights about optimal strategies and builds""",
        }

    def build_dynamic_prompt(
        self,
        conversation_memory: ConversationMemory,
        current_message: str,
        user_profile: Dict[str, Any] = None,
    ) -> str:
        """Build a dynamic, context-aware prompt"""

        # Analyze conversation context
        context_type = self._analyze_context_type(conversation_memory, current_message)
        base_prompt = self.base_prompts[context_type]

        # Add user personalization
        if user_profile:
            personalization = self._build_personalization_context(user_profile)
            if personalization:
                base_prompt += f"\n\nUser communication preferences: {personalization}"

        # Add conversation memory context
        memory_context = self._build_memory_context(conversation_memory)
        if memory_context:
            base_prompt += f"\n\nConversation memory: {memory_context}"

        # Add current interaction guidance
        interaction_guidance = self._build_interaction_guidance(
            current_message, conversation_memory
        )
        base_prompt += f"\n\n{interaction_guidance}"

        # Add response style guidance
        style_guidance = self._build_style_guidance(
            conversation_memory, current_message
        )
        base_prompt += f"\n\nResponse style: {style_guidance}"

        return base_prompt

    def _analyze_context_type(self, memory: ConversationMemory, message: str) -> str:
        """Analyze what type of conversation context this is"""
        message_lower = message.lower()

        # Check for technical/gaming content
        technical_keywords = [
            "how",
            "why",
            "explain",
            "stellaris",
            "strategy",
            "mechanics",
            "build",
            "optimize",
        ]
        if any(keyword in message_lower for keyword in technical_keywords):
            if any(
                game_term in message_lower
                for game_term in ["stellaris", "empire", "species", "fleet"]
            ):
                return "strategic"
            else:
                return "technical"

        # Check for emotional/support content
        support_keywords = [
            "help",
            "confused",
            "frustrated",
            "problem",
            "issue",
            "stuck",
            "don't understand",
        ]
        if any(keyword in message_lower for keyword in support_keywords):
            return "supportive"

        # Default to conversational
        return "conversational"

    def _build_personalization_context(self, user_profile: Dict[str, Any]) -> str:
        """Build personalization context from user profile"""
        personalizations = []

        if user_profile.get("communication_style"):
            style = user_profile["communication_style"]
            personalizations.append(f"prefers {style} communication")

        if user_profile.get("response_length_preference"):
            length = user_profile["response_length_preference"]
            personalizations.append(f"likes {length} responses")

        if user_profile.get("preferred_topics"):
            topics = list(user_profile["preferred_topics"].keys())[:3]
            if topics:
                personalizations.append(f"interested in {', '.join(topics)}")

        return "; ".join(personalizations) if personalizations else ""

    def _build_memory_context(self, memory: ConversationMemory) -> str:
        """Build context from conversation memory"""
        context_parts = []

        # Recent themes
        if memory.conversation_themes:
            themes = list(memory.conversation_themes)[-3:]
            context_parts.append(f"Recent topics: {', '.join(themes)}")

        # Important past points
        if memory.important_messages:
            recent_important = memory.important_messages[-2:]
            important_points = []
            for msg in recent_important:
                if len(msg["content"]) > 50:
                    summary = (
                        msg["content"][:100] + "..."
                        if len(msg["content"]) > 100
                        else msg["content"]
                    )
                    important_points.append(summary)
            if important_points:
                context_parts.append(
                    f"Important previous points: {' | '.join(important_points)}"
                )

        return "; ".join(context_parts) if context_parts else ""

    def _build_interaction_guidance(
        self, message: str, memory: ConversationMemory
    ) -> str:
        """Build guidance for this specific interaction"""
        guidance = "For this response:"

        # Message length adaptation
        if len(message) < 30:
            guidance += (
                " User sent a brief message, so keep response concise but helpful."
            )
        elif len(message) > 150:
            guidance += " User provided detailed input, so provide a thorough response."

        # Question detection
        if "?" in message:
            guidance += " User asked a question - provide a clear, direct answer."

        # Conversation flow
        recent_messages = list(memory.messages)[-3:] if memory.messages else []
        if len(recent_messages) >= 2:
            guidance += " Continue the natural flow of your ongoing conversation."

        return guidance

    def _build_style_guidance(self, memory: ConversationMemory, message: str) -> str:
        """Build response style guidance"""
        style_elements = []

        # Analyze user's communication patterns
        if memory.messages:
            recent_user_messages = [
                msg for msg in list(memory.messages)[-5:] if msg["role"] == "user"
            ]

            if recent_user_messages:
                # Check emoji usage
                user_uses_emojis = any(
                    any(ord(char) > 127 for char in msg["content"])
                    for msg in recent_user_messages
                )
                if user_uses_emojis:
                    style_elements.append("user likes emojis, use them appropriately")
                else:
                    style_elements.append(
                        "user doesn't use emojis, keep response clean"
                    )

                # Check formality level
                avg_length = sum(
                    len(msg["content"]) for msg in recent_user_messages
                ) / len(recent_user_messages)
                if avg_length > 100:
                    style_elements.append("match user's detailed communication style")
                else:
                    style_elements.append("keep responses conversational and concise")

        # Default style guidance
        if not style_elements:
            style_elements.append("be natural and conversational")

        return "; ".join(style_elements)


class OptimizedAIEngine:
    """Next-generation AI engine with enhanced architecture"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logger

        # Core components
        self.prompt_engine = IntelligentPromptEngine()
        self.conversation_memories: Dict[int, ConversationMemory] = {}
        self.user_profiles: Dict[int, Dict[str, Any]] = {}

        # AI provider management
        self.ai_client = None
        self.available_models = [
            OptimizedAIProvider.DEEPSEEK_R1,
            OptimizedAIProvider.DEEPSEEK_V3,
            OptimizedAIProvider.QWEN_QWQ,
            OptimizedAIProvider.GPT_4O_MINI,
            OptimizedAIProvider.CLAUDE_HAIKU,
        ]
        self.current_model = OptimizedAIProvider.DEEPSEEK_R1

        # Performance optimization
        self.response_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        self.max_cache_size = 1000

        # Quality tracking
        self.quality_metrics: Dict[str, List[float]] = defaultdict(list)
        self.model_performance: Dict[str, Dict[str, float]] = defaultdict(dict)

        # Token optimization
        self.max_tokens = 1000  # Optimized token limit
        self.temperature = 0.7
        self.token_usage_tracking: Dict[str, int] = defaultdict(int)

        # Thread pool for async operations
        self.thread_pool = ThreadPoolExecutor(max_workers=3)

        self._initialize_ai_client()

        logger.info("Optimized AI Engine initialized successfully")

    def _initialize_ai_client(self):
        """Initialize the AI client with optimized configuration"""
        try:
            if UNIVERSAL_AI_AVAILABLE:
                self.ai_client = UniversalAIClient(
                    api_key=os.getenv("AI_API_KEY"),
                    base_url=os.getenv("AI_BASE_URL", "https://openrouter.ai/api/v1"),
                    model=self.current_model.value,
                    provider_name="optimized_engine",
                )

                if self.ai_client.is_available():
                    logger.info(
                        f"✅ Optimized AI client initialized with {self.current_model.value}"
                    )
                else:
                    logger.error("❌ AI client not available - missing API key")
            else:
                logger.error("❌ Universal AI client not available")

        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            self.ai_client = None

    async def process_conversation(
        self,
        message: str,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        context_data: Dict[str, Any] = None,
    ) -> str:
        """Process conversation with enhanced optimization"""
        start_time = time.time()

        try:
            # Get or create conversation memory
            memory = self._get_conversation_memory(user_id)
            user_profile = self._get_user_profile(user_id)

            # Check cache first
            cache_key = self._generate_cache_key(message, user_id, memory)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                logger.debug(f"Cache hit for user {user_id}")
                return cached_response

            # Extract themes and update memory
            themes = self._extract_themes(message)
            memory.conversation_themes.update(themes)

            # Add user message to memory
            memory.add_message(
                "user",
                message,
                {"themes": themes, "timestamp": datetime.now(timezone.utc).isoformat()},
            )

            # Generate optimized response
            response = await self._generate_optimized_response(
                message, memory, user_profile
            )

            # Add AI response to memory
            memory.add_message("assistant", response)

            # Update user profile
            self._update_user_profile(user_id, message, response, themes)

            # Cache the response
            self._cache_response(cache_key, response)

            # Track performance
            response_time = (time.time() - start_time) * 1000
            self._track_performance("response_time", response_time)

            logger.debug(
                f"Generated response for user {user_id} in {response_time:.2f}ms"
            )
            return response

        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            return self._get_fallback_response(message)

    def _get_conversation_memory(self, user_id: int) -> ConversationMemory:
        """Get or create conversation memory for user"""
        if user_id not in self.conversation_memories:
            self.conversation_memories[user_id] = ConversationMemory(user_id=user_id)
        return self.conversation_memories[user_id]

    def _get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get or create user profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "communication_style": "balanced",
                "response_length_preference": "medium",
                "preferred_topics": {},
                "interaction_count": 0,
                "engagement_score": 0.5,
                "last_interaction": datetime.now(timezone.utc).isoformat(),
            }
        return self.user_profiles[user_id]

    def _extract_themes(self, message: str) -> Set[str]:
        """Extract conversation themes from message"""
        message_lower = message.lower()
        themes = set()

        theme_keywords = {
            "stellaris": [
                "stellaris",
                "empire",
                "species",
                "galactic",
                "federation",
                "fleet",
            ],
            "space": [
                "space",
                "cosmos",
                "universe",
                "star",
                "planet",
                "galaxy",
                "astronomy",
            ],
            "gaming": ["game", "gaming", "play", "strategy", "multiplayer", "build"],
            "science": ["science", "research", "theory", "experiment", "discovery"],
            "technology": [
                "tech",
                "technology",
                "ai",
                "computer",
                "software",
                "algorithm",
            ],
            "help": ["help", "assistance", "support", "guide", "tutorial", "how to"],
            "strategy": [
                "strategy",
                "tactics",
                "plan",
                "optimize",
                "efficient",
                "best",
            ],
        }

        for theme, keywords in theme_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                themes.add(theme)

        return themes

    def _generate_cache_key(
        self, message: str, user_id: int, memory: ConversationMemory
    ) -> str:
        """Generate cache key for response"""
        # Include message, recent context, and user themes
        context_str = ""
        if memory.messages:
            recent_messages = list(memory.messages)[-3:]
            context_str = "|".join([msg["content"][:50] for msg in recent_messages])

        themes_str = "|".join(sorted(memory.conversation_themes))
        cache_input = f"{message}|{context_str}|{themes_str}|{user_id}"

        return hashlib.md5(cache_input.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if available and fresh"""
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                return cached_data["response"]
            else:
                # Remove expired cache
                del self.response_cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, response: str):
        """Cache response with TTL"""
        # Manage cache size
        if len(self.response_cache) >= self.max_cache_size:
            # Remove oldest entries
            oldest_key = min(
                self.response_cache.keys(),
                key=lambda k: self.response_cache[k]["timestamp"],
            )
            del self.response_cache[oldest_key]

        self.response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time(),
        }

    async def _generate_optimized_response(
        self, message: str, memory: ConversationMemory, user_profile: Dict[str, Any]
    ) -> str:
        """Generate optimized AI response"""
        if not self.ai_client or not self.ai_client.is_available():
            return self._get_fallback_response(message)

        try:
            # Build dynamic prompt
            system_prompt = self.prompt_engine.build_dynamic_prompt(
                memory, message, user_profile
            )

            # Get relevant conversation context
            context_messages = memory.get_relevant_context(message, max_context=8)

            # Prepare messages for AI
            messages = [{"role": "system", "content": system_prompt}]

            # Add context messages (skip system messages to avoid duplication)
            for msg in context_messages:
                if msg["role"] != "system":
                    messages.append({"role": msg["role"], "content": msg["content"]})

            # Add current message
            messages.append({"role": "user", "content": message})

            # Generate response with optimized parameters
            response = await self.ai_client.chat_completion(
                messages=messages,
                model=self.current_model.value,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            # Track token usage
            if response.tokens_used:
                self.token_usage_tracking[
                    self.current_model.value
                ] += response.tokens_used

            # Post-process response
            processed_response = self._post_process_response(
                response.content, memory, user_profile
            )

            # Evaluate response quality
            quality = self._evaluate_response_quality(
                message, processed_response, memory
            )
            self._track_performance("response_quality", quality.overall_score)

            return processed_response

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._get_fallback_response(message)

    def _post_process_response(
        self, response: str, memory: ConversationMemory, user_profile: Dict[str, Any]
    ) -> str:
        """Post-process AI response for optimization"""
        # Clean up response
        response = response.strip()

        # Remove any system artifacts
        if response.startswith("Assistant:") or response.startswith("AI:"):
            response = response.split(":", 1)[1].strip()

        # Length optimization based on user preference
        length_pref = user_profile.get("response_length_preference", "medium")
        if length_pref == "short" and len(response) > 200:
            # Summarize if too long for user preference
            sentences = response.split(". ")
            if len(sentences) > 2:
                response = ". ".join(sentences[:2]) + "."

        # Emoji optimization based on user patterns
        if memory.messages:
            recent_user_messages = [
                msg for msg in list(memory.messages)[-5:] if msg["role"] == "user"
            ]
            user_uses_emojis = any(
                any(ord(char) > 127 for char in msg["content"])
                for msg in recent_user_messages
            )

            # Add contextual emojis if user uses them
            if user_uses_emojis and not any(ord(char) > 127 for char in response):
                if any(
                    theme in memory.conversation_themes
                    for theme in ["space", "stellaris"]
                ):
                    if len(response) < 100:
                        response += " 🌌"
                    elif "strategy" in response.lower() or "tip" in response.lower():
                        response += " ⚡"
                elif "help" in memory.conversation_themes:
                    response += " 💫"

        return response

    def _evaluate_response_quality(
        self, message: str, response: str, memory: ConversationMemory
    ) -> ResponseQuality:
        """Evaluate response quality for optimization"""
        quality = ResponseQuality()

        # Coherence: Does response make sense?
        quality.coherence_score = self._evaluate_coherence(message, response)

        # Relevance: Is response relevant to message and context?
        quality.relevance_score = self._evaluate_relevance(message, response, memory)

        # Engagement: Is response engaging and interesting?
        quality.engagement_score = self._evaluate_engagement(response)

        # Personalization: Is response adapted to user?
        quality.personalization_score = self._evaluate_personalization(response, memory)

        # Calculate overall score
        quality.calculate_overall()

        return quality

    def _evaluate_coherence(self, message: str, response: str) -> float:
        """Evaluate response coherence"""
        score = 0.5  # Base score

        # Check if response addresses the message
        if "?" in message and any(
            word in response.lower()
            for word in ["yes", "no", "because", "due to", "result"]
        ):
            score += 0.2

        # Check for logical flow
        if len(response.split(". ")) >= 2:  # Multi-sentence responses
            score += 0.1

        # Check for contradictions (simple check)
        contradiction_pairs = [("yes", "no"), ("always", "never"), ("can", "cannot")]
        for word1, word2 in contradiction_pairs:
            if word1 in response.lower() and word2 in response.lower():
                score -= 0.2
                break

        return max(0.0, min(1.0, score))

    def _evaluate_relevance(
        self, message: str, response: str, memory: ConversationMemory
    ) -> float:
        """Evaluate response relevance"""
        score = 0.3  # Base score

        # Keyword overlap between message and response
        message_words = set(message.lower().split())
        response_words = set(response.lower().split())
        overlap = len(message_words.intersection(response_words))
        score += min(0.3, overlap * 0.05)

        # Theme relevance
        message_themes = self._extract_themes(message)
        if message_themes:
            response_themes = self._extract_themes(response)
            theme_overlap = len(message_themes.intersection(response_themes))
            score += min(0.2, theme_overlap * 0.1)

        # Context relevance
        if memory.conversation_themes:
            for theme in memory.conversation_themes:
                if theme in response.lower():
                    score += 0.1
                    break

        return max(0.0, min(1.0, score))

    def _evaluate_engagement(self, response: str) -> float:
        """Evaluate response engagement"""
        score = 0.3  # Base score

        # Length factor (not too short, not too long)
        length = len(response)
        if 50 <= length <= 300:
            score += 0.2
        elif length < 20:
            score -= 0.1

        # Engaging elements
        engaging_elements = ["?", "!", "interesting", "fascinating", "amazing", "great"]
        for element in engaging_elements:
            if element in response.lower():
                score += 0.1
                break

        # Specific and actionable content
        actionable_words = ["try", "consider", "you can", "suggest", "recommend", "tip"]
        if any(word in response.lower() for word in actionable_words):
            score += 0.2

        return max(0.0, min(1.0, score))

    def _evaluate_personalization(
        self, response: str, memory: ConversationMemory
    ) -> float:
        """Evaluate response personalization"""
        score = 0.4  # Base score

        # Reference to conversation history
        if len(memory.messages) > 2:
            recent_topics = set()
            for msg in list(memory.messages)[-5:]:
                if msg["role"] == "user":
                    recent_topics.update(self._extract_themes(msg["content"]))

            # Check if response references recent topics
            response_themes = self._extract_themes(response)
            if recent_topics.intersection(response_themes):
                score += 0.3

        # Adaptive language style
        if memory.messages:
            user_messages = [msg for msg in memory.messages if msg["role"] == "user"]
            if user_messages:
                # Check if response matches user's communication style
                avg_user_length = sum(
                    len(msg["content"]) for msg in user_messages[-3:]
                ) / min(3, len(user_messages))
                response_length = len(response)

                # Reward matching message length style
                if abs(avg_user_length - response_length) < avg_user_length * 0.5:
                    score += 0.2

        return max(0.0, min(1.0, score))

    def _update_user_profile(
        self, user_id: int, message: str, response: str, themes: Set[str]
    ):
        """Update user profile based on interaction"""
        profile = self.user_profiles[user_id]

        # Update interaction count
        profile["interaction_count"] += 1

        # Update preferred topics
        for theme in themes:
            if theme in profile["preferred_topics"]:
                profile["preferred_topics"][theme] += 0.1
            else:
                profile["preferred_topics"][theme] = 0.1

        # Update communication style preferences
        message_length = len(message)
        if message_length < 50:
            profile["response_length_preference"] = "short"
        elif message_length > 150:
            profile["response_length_preference"] = "long"
        else:
            profile["response_length_preference"] = "medium"

        # Update last interaction
        profile["last_interaction"] = datetime.now(timezone.utc).isoformat()

    def _track_performance(self, metric_name: str, value: float):
        """Track performance metrics"""
        self.quality_metrics[metric_name].append(value)

        # Keep only recent metrics (last 100 values)
        if len(self.quality_metrics[metric_name]) > 100:
            self.quality_metrics[metric_name] = self.quality_metrics[metric_name][-100:]

    def _get_fallback_response(self, message: str) -> str:
        """Generate fallback response when AI is unavailable"""
        fallback_responses = [
            "I'm experiencing some technical difficulties, but I'm here to help. Could you try rephrasing your question?",
            "Having a brief connection issue on my end. Let me try to help you with what I can process.",
            "I'm having trouble accessing my full capabilities right now, but I'll do my best to assist you.",
            "Technical hiccup detected! I'm working on getting back to full functionality. How can I help in the meantime?",
            "Experiencing some system delays, but I'm still here. What would you like to know?",
        ]

        import random

        return random.choice(fallback_responses)

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        metrics = {}

        # Quality metrics
        for metric_name, values in self.quality_metrics.items():
            if values:
                metrics[f"avg_{metric_name}"] = sum(values) / len(values)
                metrics[f"recent_{metric_name}"] = (
                    values[-10:] if len(values) >= 10 else values
                )

        # Token usage
        metrics["token_usage"] = dict(self.token_usage_tracking)

        # Cache performance
        cache_hits = sum(
            1
            for data in self.response_cache.values()
            if time.time() - data["timestamp"] < self.cache_ttl
        )
        metrics["cache_hit_rate"] = cache_hits / max(1, len(self.response_cache)) * 100

        # User engagement
        metrics["active_users"] = len(self.conversation_memories)
        metrics["total_conversations"] = sum(
            len(memory.messages) for memory in self.conversation_memories.values()
        )

        # Model performance
        metrics["current_model"] = self.current_model.value
        metrics["model_performance"] = dict(self.model_performance)

        return metrics

    async def optimize_model_selection(self) -> str:
        """Dynamically optimize model selection based on performance"""
        if not self.quality_metrics["response_quality"]:
            return self.current_model.value

        current_quality = sum(self.quality_metrics["response_quality"][-10:]) / min(
            10, len(self.quality_metrics["response_quality"])
        )

        # If current model is performing well, stick with it
        if current_quality > 0.8:
            logger.info(
                f"Current model {self.current_model.value} performing well (quality: {current_quality:.2f})"
            )
            return self.current_model.value

        # If performance is poor, consider switching
        if current_quality < 0.6:
            logger.warning(
                f"Current model {self.current_model.value} underperforming (quality: {current_quality:.2f})"
            )

            # Try next available model
            current_index = self.available_models.index(self.current_model)
            next_index = (current_index + 1) % len(self.available_models)
            new_model = self.available_models[next_index]

            logger.info(f"Switching to model: {new_model.value}")
            self.current_model = new_model

            # Update AI client
            if self.ai_client:
                self.ai_client.model = new_model.value

        return self.current_model.value

    async def cleanup_memory(self):
        """Clean up old conversation memories to maintain performance"""
        current_time = datetime.now(timezone.utc)
        cleanup_threshold = timedelta(days=7)  # Clean conversations older than 7 days

        users_to_cleanup = []
        for user_id, memory in self.conversation_memories.items():
            if current_time - memory.last_interaction > cleanup_threshold:
                users_to_cleanup.append(user_id)

        for user_id in users_to_cleanup:
            # Archive important messages before cleanup
            memory = self.conversation_memories[user_id]
            if memory.important_messages:
                # Keep important messages in a compressed format
                archived_important = memory.important_messages[
                    -5:
                ]  # Keep last 5 important messages

                # Create new memory with just important messages
                new_memory = ConversationMemory(user_id=user_id)
                for msg in archived_important:
                    new_memory.important_messages.append(msg)

                self.conversation_memories[user_id] = new_memory
                logger.info(f"Archived conversation memory for user {user_id}")
            else:
                del self.conversation_memories[user_id]
                logger.info(f"Cleaned up conversation memory for user {user_id}")


# Global optimized engine instance
_optimized_engine: Optional[OptimizedAIEngine] = None


def get_optimized_engine() -> OptimizedAIEngine:
    """Get or create the global optimized AI engine"""
    global _optimized_engine
    if _optimized_engine is None:
        _optimized_engine = OptimizedAIEngine()
    return _optimized_engine


def initialize_optimized_engine(config: Dict[str, Any] = None) -> OptimizedAIEngine:
    """Initialize the global optimized AI engine with configuration"""
    global _optimized_engine
    _optimized_engine = OptimizedAIEngine(config)
    return _optimized_engine


# Convenience functions
async def process_optimized_conversation(message: str, user_id: int, **kwargs) -> str:
    """Process conversation using optimized engine"""
    engine = get_optimized_engine()
    return await engine.process_conversation(message, user_id, **kwargs)


async def get_optimized_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics from optimized engine"""
    engine = get_optimized_engine()
    return await engine.get_performance_metrics()


if __name__ == "__main__":
    # Test the optimized engine
    async def test_optimized_engine():
        print("🧪 Testing Optimized AI Engine...")

        engine = OptimizedAIEngine()

        # Test conversation processing
        test_message = (
            "Hello! Can you help me understand Stellaris fleet composition strategies?"
        )
        response = await engine.process_conversation(test_message, user_id=12345)

        print(f"Test Message: {test_message}")
        print(f"Response: {response}")

        # Test performance metrics
        metrics = await engine.get_performance_metrics()
        print(f"Performance Metrics: {metrics}")

    asyncio.run(test_optimized_engine())
