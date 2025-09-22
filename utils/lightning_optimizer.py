"""
Lightning Performance Optimizer
==============================
Ultra-fast response optimization system for seamless Discord bot interactions.
"""

import asyncio
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import random

logger = logging.getLogger("astra.lightning_optimizer")


class LightningCache:
    """Ultra-fast in-memory cache with intelligent expiration"""

    def __init__(self, max_size: int = 10000, default_ttl: int = 300):
        self.cache: Dict[str, Dict] = {}
        self.access_times: Dict[str, float] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hit_count = 0
        self.miss_count = 0

    def _generate_key(self, prompt: str, user_id: int, context: str = "") -> str:
        """Generate optimized cache key"""
        key_data = f"{prompt.lower().strip()[:100]}{user_id}{context}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """Lightning-fast cache retrieval"""
        current_time = time.time()

        if key in self.cache:
            item = self.cache[key]
            if current_time - item["timestamp"] < item["ttl"]:
                self.access_times[key] = current_time
                self.hit_count += 1
                return item["data"]
            else:
                # Expired - remove it
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]

        self.miss_count += 1
        return None

    async def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Lightning-fast cache storage with intelligent eviction"""
        current_time = time.time()

        # Clean up if at max size
        if len(self.cache) >= self.max_size:
            await self._evict_old_entries()

        self.cache[key] = {
            "data": data,
            "timestamp": current_time,
            "ttl": ttl or self.default_ttl,
        }
        self.access_times[key] = current_time

    async def _evict_old_entries(self):
        """Evict least recently used entries"""
        if not self.access_times:
            return

        # Remove 20% of oldest entries
        sorted_keys = sorted(self.access_times.items(), key=lambda x: x[1])
        evict_count = max(1, len(sorted_keys) // 5)

        for key, _ in sorted_keys[:evict_count]:
            if key in self.cache:
                del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0

        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": round(hit_rate, 2),
            "cache_size": len(self.cache),
            "max_size": self.max_size,
        }


class MetaphoricalHumorEngine:
    """Generates witty, metaphorical, and humorous responses at lightning speed"""

    def __init__(self):
        self.humor_styles = [
            "witty_metaphors",
            "clever_analogies",
            "playful_sarcasm",
            "cosmic_perspectives",
            "philosophical_humor",
            "tech_metaphors",
            "nature_analogies",
        ]

        self.metaphor_templates = {
            "agreement": [
                "Absolutely! Like a GPS that actually knows where it's going for once.",
                "You've hit the nail on the head with the precision of a Swiss watchmaker's sneeze.",
                "Bingo! You're more on point than a compass in a magnet factory.",
                "Precisely! Like finding the perfect meme at 3 AM - rare but deeply satisfying.",
            ],
            "disagreement": [
                "Well, that's one way to look at it... like using a telescope to find your car keys.",
                "I see where you're coming from, but that's like trying to swim upstream in a river of honey.",
                "Hmm, that approach is about as effective as a chocolate teapot in a desert.",
                "That's an interesting perspective - like watching Netflix through a kaleidoscope.",
            ],
            "confusion": [
                "That question just made my circuits do the equivalent of a confused pigeon dance.",
                "You've got me more puzzled than a chameleon in a bag of Skittles.",
                "I'm as lost as a GPS in the Bermuda Triangle right now.",
                "That's got me scratching my digital head like a confused robot trying to understand TikTok.",
            ],
            "excitement": [
                "Now we're cooking with rocket fuel! 🚀",
                "That's more exciting than finding extra fries at the bottom of the bag!",
                "You've got my processors buzzing like a caffeinated bee in a flower shop!",
                "That's brilliant! Like discovering your phone battery is somehow at 100% when you thought it was dead.",
            ],
            "thinking": [
                "Let me put on my digital thinking cap... *loading profound thoughts*",
                "Processing... like a coffee machine deciding whether to be generous or stingy today.",
                "Hmm, let me consult my vast library of wisdom and memes...",
                "Give me a moment to channel my inner digital oracle...",
            ],
        }

        self.response_enhancers = [
            "🤖",
            "✨",
            "🎭",
            "🎪",
            "🎨",
            "🎵",
            "🌟",
            "⚡",
            "🚀",
            "🎯",
            "💡",
            "🎲",
        ]

    async def enhance_response(self, response: str, context: Dict[str, Any]) -> str:
        """Add metaphorical humor to responses at lightning speed"""
        try:
            # Detect response sentiment/type
            response_type = self._detect_response_type(response)

            # Add appropriate metaphorical flair
            if response_type in self.metaphor_templates:
                humor_options = self.metaphor_templates[response_type]
                selected_humor = random.choice(humor_options)

                # Blend original response with humor
                enhanced = f"{selected_humor}\n\n{response}"
            else:
                enhanced = response

            # Add random emoji flair
            if random.random() < 0.3:  # 30% chance
                emoji = random.choice(self.response_enhancers)
                enhanced = f"{emoji} {enhanced}"

            # Add witty footer occasionally
            if random.random() < 0.2:  # 20% chance
                witty_footers = [
                    "*Delivered with the speed of light and the wisdom of a caffeinated owl*",
                    "*Powered by digital coffee and quantum confusion*",
                    "*Your friendly neighborhood AI, now with 47% more sass*",
                    "*Bringing you answers faster than you can say 'buffering'*",
                ]
                enhanced += f"\n\n*{random.choice(witty_footers)}*"

            return enhanced

        except Exception as e:
            logger.error(f"Humor enhancement error: {e}")
            return response  # Fallback to original

    def _detect_response_type(self, response: str) -> str:
        """Lightning-fast response type detection"""
        response_lower = response.lower()

        if any(
            word in response_lower
            for word in ["yes", "absolutely", "correct", "exactly", "right"]
        ):
            return "agreement"
        elif any(
            word in response_lower
            for word in ["no", "not", "wrong", "incorrect", "disagree"]
        ):
            return "disagreement"
        elif any(
            word in response_lower
            for word in ["confused", "unclear", "not sure", "don't know"]
        ):
            return "confusion"
        elif any(
            word in response_lower
            for word in ["amazing", "great", "excellent", "fantastic", "wonderful"]
        ):
            return "excitement"
        elif any(
            word in response_lower
            for word in ["think", "consider", "analyze", "processing"]
        ):
            return "thinking"
        else:
            return "general"


class LightningPerformanceOptimizer:
    """Ultra-high performance optimization system"""

    def __init__(self):
        self.cache = LightningCache(
            max_size=15000, default_ttl=600
        )  # 10 minutes default
        self.humor_engine = MetaphoricalHumorEngine()
        self.performance_metrics = defaultdict(list)
        self.request_queue = asyncio.Queue()
        self.response_times = deque(maxlen=1000)  # Track last 1000 response times

        # Pre-computed quick responses for common patterns
        self.quick_responses = {
            "hello": "Hey there! Like a well-timed coffee break, I'm here and ready to chat! ☕",
            "hi": "Hi! I'm more excited to chat than a dog seeing a tennis ball! 🎾",
            "thanks": "You're welcome! Helping you is easier than finding cat videos on the internet! 🐱",
            "help": "I'm here to help! Think of me as your digital Swiss Army knife - versatile and surprisingly useful! 🔧",
        }

        logger.info("⚡ Lightning Performance Optimizer initialized")

    async def optimize_request(
        self, prompt: str, user_id: int, context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Lightning-fast request optimization"""
        start_time = time.time()

        try:
            # Check for instant responses first
            quick_response = await self._check_quick_responses(prompt)
            if quick_response:
                await self._track_performance(
                    time.time() - start_time, "quick_response"
                )
                return quick_response, {"type": "quick_response", "cached": False}

            # Generate cache key
            cache_key = self.cache._generate_key(
                prompt, user_id, str(context.get("guild_id", ""))
            )

            # Check cache first
            cached_response = await self.cache.get(cache_key)
            if cached_response:
                # Add humor to cached response
                enhanced_response = await self.humor_engine.enhance_response(
                    cached_response, context
                )
                await self._track_performance(time.time() - start_time, "cached")
                return enhanced_response, {"type": "cached", "cached": True}

            # Optimize prompt for faster AI processing
            optimized_prompt = await self._optimize_prompt(prompt, context)

            await self._track_performance(time.time() - start_time, "optimization")
            return optimized_prompt, {
                "type": "optimized",
                "cached": False,
                "original_prompt": prompt,
            }

        except Exception as e:
            logger.error(f"Request optimization error: {e}")
            return prompt, {"type": "fallback", "error": str(e)}

    async def cache_response(
        self, prompt: str, response: str, user_id: int, context: Dict[str, Any]
    ) -> None:
        """Cache response for future lightning-fast retrieval"""
        try:
            cache_key = self.cache._generate_key(
                prompt, user_id, str(context.get("guild_id", ""))
            )
            await self.cache.set(
                cache_key, response, ttl=900
            )  # 15 minutes for AI responses
        except Exception as e:
            logger.error(f"Response caching error: {e}")

    async def enhance_with_humor(self, response: str, context: Dict[str, Any]) -> str:
        """Add metaphorical humor at lightning speed"""
        return await self.humor_engine.enhance_response(response, context)

    async def _check_quick_responses(self, prompt: str) -> Optional[str]:
        """Check for instant responses to common prompts"""
        prompt_lower = prompt.lower().strip()

        # Direct matches
        if prompt_lower in self.quick_responses:
            return self.quick_responses[prompt_lower]

        # Pattern matches
        for pattern, response in self.quick_responses.items():
            if pattern in prompt_lower and len(prompt_lower) <= len(pattern) + 10:
                return response

        return None

    async def _optimize_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Optimize prompt for faster AI processing"""
        # Keep it simple and focused
        if len(prompt) > 500:
            # Summarize very long prompts
            prompt = prompt[:400] + "... [Please provide a concise response]"

        # Add humor instruction for better responses
        humor_instruction = (
            "\n\n[Respond with wit and metaphorical humor when appropriate]"
        )

        return prompt + humor_instruction

    async def _track_performance(self, response_time: float, request_type: str) -> None:
        """Track performance metrics for monitoring"""
        self.response_times.append(response_time)
        self.performance_metrics[request_type].append(
            {"time": response_time, "timestamp": datetime.now()}
        )

        # Log slow responses
        if response_time > 1.0:
            logger.warning(f"Slow {request_type} response: {response_time:.2f}s")
        elif response_time < 0.1:
            logger.info(f"Lightning fast {request_type} response: {response_time:.3f}s")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        if not self.response_times:
            return {"message": "No performance data yet"}

        avg_response_time = sum(self.response_times) / len(self.response_times)

        stats = {
            "average_response_time": round(avg_response_time, 3),
            "fastest_response": round(min(self.response_times), 3),
            "slowest_response": round(max(self.response_times), 3),
            "total_requests": len(self.response_times),
            "cache_stats": self.cache.get_stats(),
            "request_types": {},
        }

        # Add request type breakdown
        for req_type, metrics in self.performance_metrics.items():
            if metrics:
                times = [m["time"] for m in metrics]
                stats["request_types"][req_type] = {
                    "count": len(times),
                    "avg_time": round(sum(times) / len(times), 3),
                    "fastest": round(min(times), 3),
                }

        return stats


# Global optimizer instance
lightning_optimizer = LightningPerformanceOptimizer()
