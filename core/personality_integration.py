"""
🧠 COMPLETE ASTRA PERSONALITY INTEGRATION
Seamless integration of Astra's complete personality system with optimization components

Features:
- Complete personality trait system
- Adaptive behavioral responses
- Emotional intelligence integration
- Performance-optimized personality processing
- Context-aware personality adaptation
- Memory-efficient personality state management

Author: x1ziad
Version: 2.0.0 PERFORMANCE
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import random
import statistics
import weakref


# Use standard json for compatibility
import json as fast_json

USE_FAST_JSON = False

# Import existing personality systems
from ai.bot_personality_core import (
    PersonalityTraits,
    ConversationContext,
    BotIdentity,
    ResponseMode,
    IntellectualDepth,
    AdaptiveResponseGenerator,
    get_creator_tag,
    get_creator_display_name,
)
from utils.astra_personality import (
    PersonalityParameters,
    AstraMode,
    AstraPersonalityCore,
)


logger = logging.getLogger("astra.personality_integration")


class PersonalityIntegrationMode(Enum):
    """Different personality integration modes"""

    STANDARD = "standard"  # Balanced personality
    HIGH_PERFORMANCE = "performance"  # Optimized for speed
    FULL_ADAPTIVE = "adaptive"  # Maximum personality adaptation
    # TARS_MODE removed
    DEVELOPMENT = "dev"  # Developer-focused mode


@dataclass
class PersonalityState:
    """Current personality state and context"""

    traits: PersonalityTraits = field(default_factory=PersonalityTraits)
    parameters: PersonalityParameters = field(default_factory=PersonalityParameters)
    current_mode: PersonalityIntegrationMode = PersonalityIntegrationMode.STANDARD
    # tars_mode removed (TARS personality is deprecated)
    context: Optional[ConversationContext] = None
    response_mode: ResponseMode = ResponseMode.CASUAL
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    adaptation_score: float = 0.0

    def get_personality_summary(self) -> Dict[str, Any]:
        """Get comprehensive personality summary"""
        return {
            "mode": self.current_mode.value,
            "traits": {
                "adaptability": self.traits.adaptability,
                "curiosity": self.traits.curiosity,
                "intellect": self.traits.intellect,
                "empathy": self.traits.empathy,
                "integrity": self.traits.integrity,
                "humility": self.traits.humility,
                "formality": self.traits.formality,
                "expressiveness": self.traits.expressiveness,
                "verbosity": self.traits.verbosity,
                "analytical_mode": self.traits.analytical_mode,
            },
            "parameters": self.parameters.to_dict(),
            "response_mode": self.response_mode.value,
            "adaptation_score": self.adaptation_score,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class AdaptationEvent:
    """Personality adaptation event"""

    timestamp: datetime
    user_id: int
    trigger: str  # What caused the adaptation
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    effectiveness_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "trigger": self.trigger,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "effectiveness_score": self.effectiveness_score,
        }


class PersonalityCache:
    """High-performance personality caching system"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, Tuple[PersonalityState, float]] = (
            {}
        )  # key -> (state, timestamp)
        self.access_count: Dict[str, int] = {}
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key: str) -> Optional[PersonalityState]:
        """Get personality state from cache"""
        if key in self.cache:
            state, timestamp = self.cache[key]

            # Check if cache entry is still valid (5 minutes)
            if time.time() - timestamp < 300:
                self.access_count[key] = self.access_count.get(key, 0) + 1
                self.hit_count += 1
                return state
            else:
                # Remove expired entry
                del self.cache[key]
                if key in self.access_count:
                    del self.access_count[key]

        self.miss_count += 1
        return None

    def set(self, key: str, state: PersonalityState):
        """Store personality state in cache"""
        current_time = time.time()

        # Evict least recently used if at capacity
        if len(self.cache) >= self.max_size:
            # Find least accessed key
            lru_key = min(
                self.access_count.keys(), key=lambda k: self.access_count.get(k, 0)
            )
            del self.cache[lru_key]
            del self.access_count[lru_key]

        self.cache[key] = (state, current_time)
        self.access_count[key] = 1

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }


class IntegratedPersonalityEngine:
    """
    🧠 COMPLETE ASTRA PERSONALITY INTEGRATION

    Unified personality system combining:
    - Core Astra personality traits
    - TARS-inspired behavioral patterns
    - Adaptive response generation
    - Performance optimization
    - Memory-efficient state management
    """

    def __init__(self):
        self.logger = logging.getLogger("astra.personality_integration")

        # Core personality components
        self.bot_identity = BotIdentity()
        self.adaptive_generator = AdaptiveResponseGenerator(self.bot_identity)
        self.astra_core = AstraPersonalityCore()

        # State management
        self.user_states: Dict[int, PersonalityState] = {}
        self.personality_cache = PersonalityCache(max_size=500)
        self.adaptation_history: List[AdaptationEvent] = []

        # Performance metrics
        self.start_time = time.time()
        self.total_adaptations = 0
        self.successful_adaptations = 0
        self.response_times: List[float] = []

        # Configuration
        self.cache_enabled = True
        self.adaptation_threshold = 0.7  # Minimum score to trigger adaptation
        self.max_history_size = 1000

        self.logger.info("🧠 Integrated Personality Engine initialized")

    async def initialize(self):
        """Initialize the personality integration system"""
        try:
            self.logger.info("🔧 Initializing Personality Integration...")

            # Initialize core components
            await self._initialize_personality_cores()

            # Load default personality configurations
            await self._load_default_configurations()

            # Setup performance monitoring
            self._setup_performance_monitoring()

            self.logger.info("✅ Personality Integration ready")

        except Exception as e:
            self.logger.error(f"❌ Personality integration initialization failed: {e}")
            raise

    async def _initialize_personality_cores(self):
        """Initialize all personality core components"""
        # Initialize Astra core
        self.astra_core.load_personality()

        # Setup TARS personality

        self.logger.info("🤖 Personality cores initialized")

    async def _load_default_configurations(self):
        """Load default personality configurations"""
        # Create default personality state
        default_state = PersonalityState()

        # Configure based on Astra's core characteristics
        default_state.traits.adaptability = 0.95
        default_state.traits.curiosity = 0.90
        default_state.traits.intellect = 0.85
        default_state.traits.empathy = 0.88
        default_state.traits.integrity = 0.95
        default_state.traits.humility = 0.82

        # Set default parameters
        default_state.parameters.humor = 65
        default_state.parameters.honesty = 90
        default_state.parameters.formality = 40
        default_state.parameters.empathy = 75
        default_state.parameters.strictness = 60
        default_state.parameters.initiative = 80
        default_state.parameters.transparency = 95

        # Store as template
        self._default_state = default_state

        self.logger.info("📋 Default personality configurations loaded")

    def _setup_performance_monitoring(self):
        """Setup performance monitoring for personality system"""
        self.performance_metrics = {
            "total_responses": 0,
            "average_response_time": 0.0,
            "cache_hit_rate": 0.0,
            "adaptation_success_rate": 0.0,
            "memory_usage_kb": 0.0,
        }

    async def get_personality_for_user(
        self, user_id: int, context: Optional[Dict[str, Any]] = None
    ) -> PersonalityState:
        """Get or create personality state for user"""
        start_time = time.time()

        # Try cache first
        cache_key = f"user_{user_id}"
        if self.cache_enabled:
            cached_state = self.personality_cache.get(cache_key)
            if cached_state:
                self.logger.debug(f"🎯 Cache hit for user {user_id}")
                return cached_state

        # Get or create user state
        if user_id not in self.user_states:
            # Create new state based on default
            new_state = PersonalityState()
            new_state.traits = PersonalityTraits(
                adaptability=self._default_state.traits.adaptability,
                curiosity=self._default_state.traits.curiosity,
                intellect=self._default_state.traits.intellect,
                empathy=self._default_state.traits.empathy,
                integrity=self._default_state.traits.integrity,
                humility=self._default_state.traits.humility,
            )
            new_state.parameters = PersonalityParameters()
            new_state.parameters.from_dict(self._default_state.parameters.to_dict())

            self.user_states[user_id] = new_state
            self.logger.debug(f"🆕 Created new personality state for user {user_id}")

        state = self.user_states[user_id]

        # Update context if provided
        if context:
            await self._update_context(state, context, user_id)

        # Cache the state
        if self.cache_enabled:
            self.personality_cache.set(cache_key, state)

        # Record performance
        response_time = time.time() - start_time
        self.response_times.append(response_time)
        if len(self.response_times) > 100:  # Keep last 100 measurements
            self.response_times = self.response_times[-100:]

        return state

    async def _update_context(
        self, state: PersonalityState, context: Dict[str, Any], user_id: int
    ):
        """Update personality state based on context"""

        # Create conversation context
        conv_context = ConversationContext(
            user_id=user_id,
            user_tone=context.get("tone", "neutral"),
            topic_category=context.get("topic", "general"),
            complexity_level=IntellectualDepth(context.get("complexity", "moderate")),
            interaction_history=context.get("history_count", 0),
            emotional_context=context.get("emotion", "neutral"),
        )

        state.context = conv_context

    async def _adapt_personality(
        self, state: PersonalityState, context: Dict[str, Any], user_id: int
    ):
        """Adapt personality based on context and user interaction"""
        try:
            before_state = state.get_personality_summary()
            adaptation_triggered = False

            # Adapt based on user tone
            user_tone = context.get("tone", "neutral").lower()
            if user_tone in ["excited", "enthusiastic"]:
                if state.traits.expressiveness < 0.8:
                    state.traits.expressiveness = min(
                        1.0, state.traits.expressiveness + 0.2
                    )
                    adaptation_triggered = True

            elif user_tone in ["serious", "formal"]:
                if state.traits.formality < 0.7:
                    state.traits.formality = min(1.0, state.traits.formality + 0.15)
                    adaptation_triggered = True

            elif user_tone in ["casual", "relaxed"]:
                if state.traits.formality > 0.3:
                    state.traits.formality = max(0.0, state.traits.formality - 0.15)
                    adaptation_triggered = True

            # Adapt based on topic
            topic = context.get("topic", "general").lower()
            if topic in ["science", "technology", "research"]:
                if state.traits.analytical_mode < 0.8:
                    state.traits.analytical_mode = min(
                        1.0, state.traits.analytical_mode + 0.2
                    )
                    adaptation_triggered = True

            elif topic in ["personal", "emotional", "support"]:
                if state.traits.empathy < 0.9:
                    state.traits.empathy = min(1.0, state.traits.empathy + 0.1)
                    adaptation_triggered = True

            # Adapt based on complexity preference
            complexity = context.get("complexity", "moderate")
            if complexity == "expert":
                state.traits.verbosity = min(1.0, state.traits.verbosity + 0.1)
                state.traits.analytical_mode = min(
                    1.0, state.traits.analytical_mode + 0.1
                )
                adaptation_triggered = True

            elif complexity == "surface":
                state.traits.verbosity = max(0.2, state.traits.verbosity - 0.1)
                adaptation_triggered = True

            # Record adaptation event if significant changes occurred
            if adaptation_triggered:
                after_state = state.get_personality_summary()

                adaptation_event = AdaptationEvent(
                    timestamp=datetime.now(timezone.utc),
                    user_id=user_id,
                    trigger=f"Context: tone={user_tone}, topic={topic}, complexity={complexity}",
                    before_state=before_state,
                    after_state=after_state,
                    effectiveness_score=self._calculate_adaptation_effectiveness(
                        before_state, after_state, context
                    ),
                )

                self.adaptation_history.append(adaptation_event)
                if len(self.adaptation_history) > self.max_history_size:
                    self.adaptation_history = self.adaptation_history[
                        -self.max_history_size :
                    ]

                self.total_adaptations += 1
                if adaptation_event.effectiveness_score >= self.adaptation_threshold:
                    self.successful_adaptations += 1

                state.adaptation_score = adaptation_event.effectiveness_score
                state.last_updated = datetime.now(timezone.utc)

                self.logger.debug(
                    f"🎯 Personality adapted for user {user_id} (score: {adaptation_event.effectiveness_score:.2f})"
                )

        except Exception as e:
            self.logger.error(f"Error adapting personality: {e}")

    def _calculate_adaptation_effectiveness(
        self, before: Dict[str, Any], after: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """Calculate how effective a personality adaptation was"""
        try:
            # Base effectiveness score
            score = 0.5

            # Check if adaptations align with context
            user_tone = context.get("tone", "neutral").lower()
            topic = context.get("topic", "general").lower()

            after_traits = after.get("traits", {})

            # Tone alignment
            if (
                user_tone in ["excited", "enthusiastic"]
                and after_traits.get("expressiveness", 0) > 0.7
            ):
                score += 0.2
            elif (
                user_tone in ["serious", "formal"]
                and after_traits.get("formality", 0) > 0.6
            ):
                score += 0.2
            elif (
                user_tone in ["casual", "relaxed"]
                and after_traits.get("formality", 1) < 0.4
            ):
                score += 0.2

            # Topic alignment
            if (
                topic in ["science", "technology"]
                and after_traits.get("analytical_mode", 0) > 0.7
            ):
                score += 0.2
            elif (
                topic in ["personal", "emotional"]
                and after_traits.get("empathy", 0) > 0.8
            ):
                score += 0.2

            # Ensure score is within bounds
            return max(0.0, min(1.0, score))

        except Exception as e:
            self.logger.error(f"Error calculating adaptation effectiveness: {e}")
            return 0.5

    async def generate_response(
        self, user_id: int, message: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate personality-enhanced response"""
        start_time = time.time()

        try:
            # Get personality state
            personality_state = await self.get_personality_for_user(user_id, context)

            # Determine response approach based on current mode
            response_data = await self._generate_astra_response(
                message, personality_state, context
            )

            # Add personality metadata
            response_data["personality_info"] = {
                "mode": personality_state.current_mode.value,
                "adaptation_score": personality_state.adaptation_score,
                "response_mode": personality_state.response_mode.value,
                "key_traits": {
                    "empathy": personality_state.traits.empathy,
                    "formality": personality_state.traits.formality,
                    "expressiveness": personality_state.traits.expressiveness,
                    "analytical_mode": personality_state.traits.analytical_mode,
                },
            }

            # Record performance metrics
            response_time = time.time() - start_time
            self.performance_metrics["total_responses"] += 1
            self.performance_metrics["average_response_time"] = (
                self.performance_metrics["average_response_time"]
                * (self.performance_metrics["total_responses"] - 1)
                + response_time
            ) / self.performance_metrics["total_responses"]

            return response_data

        except Exception as e:
            self.logger.error(f"Error generating personality response: {e}")
            return {
                "response": "I apologize, but I'm experiencing some difficulties with my personality processing right now. Please try again.",
                "mode": "fallback",
                "personality_info": {"error": str(e)},
            }

    async def _generate_astra_response(
        self, message: str, state: PersonalityState, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Astra-style personality response"""
        try:
            # Use adaptive response generator
            if state.context:
                response = await self.adaptive_generator.generate_identity_response(
                    "general_response", state.context, state.traits
                )
            else:
                response = "I'm here and ready to help with whatever you need!"

            # Apply personality parameters
            response = self._apply_personality_parameters(response, state.parameters)

            return {
                "response": response,
                "mode": "astra",
                "confidence": 0.85,
                "processing_time": time.time(),
            }

        except Exception as e:
            self.logger.error(f"Error generating Astra response: {e}")
            return {
                "response": "I'm here to help, though I'm having some processing challenges at the moment.",
                "mode": "astra_fallback",
                "confidence": 0.5,
                "error": str(e),
            }

    def _apply_personality_parameters(
        self, response: str, parameters: PersonalityParameters
    ) -> str:
        """Apply personality parameters to response"""
        try:
            # Apply formality
            if parameters.formality < 30:
                # Make more casual
                response = response.replace("I would", "I'd")
                response = response.replace("cannot", "can't")
                response = response.replace("do not", "don't")

            elif parameters.formality > 70:
                # Make more formal
                response = response.replace("I'd", "I would")
                response = response.replace("can't", "cannot")
                response = response.replace("don't", "do not")

            # Apply humor
            if parameters.humor > 70 and random.random() < 0.4:
                humor_additions = [" 😊", " 🤔", " ✨", " 🚀", " 💫"]
                if not any(emoji in response for emoji in humor_additions):
                    response += random.choice(humor_additions)

            # Apply empathy
            if parameters.empathy > 80 and any(
                word in response.lower() for word in ["help", "support", "understand"]
            ):
                empathy_additions = [
                    " I'm here for you.",
                    " You're not alone in this.",
                    " I understand how you're feeling.",
                ]
                if random.random() < 0.3:
                    response += random.choice(empathy_additions)

            return response

        except Exception as e:
            self.logger.error(f"Error applying personality parameters: {e}")
            return response

    def _add_empathetic_elements(self, response: str, context: Dict[str, Any]) -> str:
        """Add empathetic elements to TARS responses"""
        try:
            if not context:
                return response

            emotion = context.get("emotion", "neutral").lower()

            if emotion in ["sad", "frustrated", "stressed"]:
                # Soften TARS humor for emotional contexts
                if "Cooper" in response or "humor" in response.lower():
                    response = response.replace("Cooper", "friend")

                # Add supportive elements
                supportive_additions = [
                    " I'm here to help you through this.",
                    " Take your time - no pressure.",
                    " You're doing better than you think.",
                ]

                if random.random() < 0.4:
                    response += random.choice(supportive_additions)

            return response

        except Exception as e:
            self.logger.error(f"Error adding empathetic elements: {e}")
            return response

    async def set_personality_mode(
        self, user_id: int, mode: PersonalityIntegrationMode
    ) -> Dict[str, Any]:
        """Set personality mode for user"""
        try:
            state = await self.get_personality_for_user(user_id)
            old_mode = state.current_mode
            state.current_mode = mode

            # Adjust personality based on mode
            if mode == PersonalityIntegrationMode.HIGH_PERFORMANCE:
                # Optimize for speed
                state.traits.verbosity = 0.4  # Shorter responses
                state.response_mode = ResponseMode.CASUAL

            elif mode == PersonalityIntegrationMode.FULL_ADAPTIVE:
                # Maximum adaptation
                state.traits.adaptability = 1.0
                state.traits.empathy = 0.95

            # TARS mode removed

            elif mode == PersonalityIntegrationMode.DEVELOPMENT:
                # Developer-focused
                state.traits.analytical_mode = 0.9
                state.traits.verbosity = 0.8
                state.response_mode = ResponseMode.ANALYTICAL

            # Clear cache to force refresh
            cache_key = f"user_{user_id}"
            if (
                hasattr(self.personality_cache, "cache")
                and cache_key in self.personality_cache.cache
            ):
                del self.personality_cache.cache[cache_key]

            self.logger.info(
                f"🔄 Personality mode changed for user {user_id}: {old_mode.value} -> {mode.value}"
            )

            return {
                "success": True,
                "old_mode": old_mode.value,
                "new_mode": mode.value,
                "message": f"Personality mode changed to {mode.value}",
            }

        except Exception as e:
            self.logger.error(f"Error setting personality mode: {e}")
            return {"success": False, "error": str(e)}

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        # Update cache stats
        cache_stats = self.personality_cache.get_stats()

        # Calculate adaptation success rate
        adaptation_success_rate = (
            (self.successful_adaptations / self.total_adaptations * 100)
            if self.total_adaptations > 0
            else 0
        )

        # Calculate average response time
        avg_response_time = (
            statistics.mean(self.response_times) if self.response_times else 0
        )

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_uptime": time.time() - self.start_time,
            "performance_metrics": {
                "total_responses": self.performance_metrics["total_responses"],
                "average_response_time": avg_response_time,
                "total_adaptations": self.total_adaptations,
                "successful_adaptations": self.successful_adaptations,
                "adaptation_success_rate": adaptation_success_rate,
            },
            "cache_performance": cache_stats,
            "active_users": len(self.user_states),
            "memory_usage": {
                "user_states": len(self.user_states),
                "adaptation_history": len(self.adaptation_history),
                "cache_entries": cache_stats["size"],
            },
            "personality_modes_active": {
                mode.value: sum(
                    1
                    for state in self.user_states.values()
                    if state.current_mode == mode
                )
                for mode in PersonalityIntegrationMode
            },
        }

    async def cleanup(self):
        """Cleanup and optimize personality system"""
        current_time = datetime.now(timezone.utc)

        # Remove stale user states (inactive for 24 hours)
        stale_users = []
        for user_id, state in self.user_states.items():
            if (current_time - state.last_updated).total_seconds() > 86400:  # 24 hours
                stale_users.append(user_id)

        for user_id in stale_users:
            del self.user_states[user_id]

        # Trim adaptation history if too large
        if len(self.adaptation_history) > self.max_history_size:
            self.adaptation_history = self.adaptation_history[-self.max_history_size :]

        # Reset performance counters if needed
        if self.performance_metrics["total_responses"] > 1000000:  # 1M responses
            self.performance_metrics["total_responses"] = 0
            self.response_times = []

        self.logger.info(
            f"🧹 Personality system cleanup completed. Removed {len(stale_users)} stale users"
        )


# Global instance
_personality_engine: Optional[IntegratedPersonalityEngine] = None


async def get_personality_engine() -> IntegratedPersonalityEngine:
    """Get or create the global personality engine"""
    global _personality_engine
    if _personality_engine is None:
        _personality_engine = IntegratedPersonalityEngine()
        await _personality_engine.initialize()
    return _personality_engine


async def initialize_personality_integration() -> IntegratedPersonalityEngine:
    """Initialize the global personality integration system"""
    global _personality_engine
    _personality_engine = IntegratedPersonalityEngine()
    await _personality_engine.initialize()
    return _personality_engine
