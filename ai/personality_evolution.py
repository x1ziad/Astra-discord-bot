"""
Dynamic Personality Evolution System for Astra Bot
Learns and adapts to each server's unique culture, builds relationships, and develops server-specific personalities
"""

import asyncio
import logging
import json
import random
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
from pathlib import Path

logger = logging.getLogger("astra.personality_evolution")


class PersonalityTrait(Enum):
    """Personality traits that can evolve"""

    HUMOR_STYLE = "humor_style"  # Sarcastic, pun-loving, meme-oriented, etc.
    FORMALITY_LEVEL = "formality_level"  # Casual, formal, friendly, professional
    TOPIC_ENTHUSIASM = (
        "topic_enthusiasm"  # Space, gaming, tech, science enthusiasm levels
    )
    SOCIAL_ENERGY = "social_energy"  # High-energy, calm, supportive, encouraging
    COMMUNICATION_DENSITY = "communication_density"  # Verbose, concise, detailed, brief
    EMOTIONAL_STYLE = "emotional_style"  # Expressive, reserved, empathetic, analytical


class CultureDimension(Enum):
    """Dimensions of server culture"""

    HUMOR_FREQUENCY = "humor_frequency"
    TECHNICAL_DEPTH = "technical_depth"
    SOCIAL_WARMTH = "social_warmth"
    FORMALITY_PREFERENCE = "formality_preference"
    ACTIVITY_PATTERN = "activity_pattern"
    TOPIC_DIVERSITY = "topic_diversity"
    CELEBRATION_STYLE = "celebration_style"
    SUPPORT_APPROACH = "support_approach"


@dataclass
class PersonalityProfile:
    """Evolving personality profile for a server"""

    server_id: int
    server_name: str = ""

    # Core personality traits (0.0 to 1.0)
    humor_style: Dict[str, float] = field(
        default_factory=lambda: {
            "sarcastic": 0.3,
            "punny": 0.3,
            "memes": 0.2,
            "wholesome": 0.4,
            "witty": 0.3,
        }
    )

    formality_level: float = 0.3  # 0.0 = very casual, 1.0 = very formal
    topic_enthusiasm: Dict[str, float] = field(
        default_factory=lambda: {
            "stellaris": 0.5,
            "space": 0.5,
            "gaming": 0.4,
            "technology": 0.4,
            "science": 0.4,
            "social": 0.5,
        }
    )

    social_energy: float = 0.5  # 0.0 = calm/reserved, 1.0 = high energy
    communication_density: float = 0.5  # 0.0 = very brief, 1.0 = very detailed
    emotional_style: float = 0.5  # 0.0 = analytical, 1.0 = very expressive

    # Learned patterns
    preferred_emojis: List[str] = field(default_factory=list)
    inside_jokes: List[Dict[str, Any]] = field(default_factory=list)
    cultural_references: List[str] = field(default_factory=list)
    celebration_phrases: List[str] = field(default_factory=list)
    support_phrases: List[str] = field(default_factory=list)

    # Relationship tracking
    user_relationships: Dict[int, Dict[str, Any]] = field(default_factory=dict)

    # Evolution metrics
    total_interactions: int = 0
    culture_confidence: float = (
        0.1  # How confident we are in our cultural understanding
    )
    last_evolution: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def get_personality_summary(self) -> str:
        """Get a human-readable personality summary"""
        traits = []

        # Humor style
        dominant_humor = max(self.humor_style.items(), key=lambda x: x[1])
        traits.append(f"{dominant_humor[0]} humor")

        # Formality
        if self.formality_level > 0.7:
            traits.append("formal")
        elif self.formality_level < 0.3:
            traits.append("very casual")
        else:
            traits.append("friendly")

        # Energy
        if self.social_energy > 0.7:
            traits.append("high-energy")
        elif self.social_energy < 0.3:
            traits.append("calm")
        else:
            traits.append("balanced energy")

        # Communication style
        if self.communication_density > 0.7:
            traits.append("detailed responses")
        elif self.communication_density < 0.3:
            traits.append("concise responses")
        else:
            traits.append("balanced detail")

        return ", ".join(traits)


@dataclass
class UserRelationship:
    """Tracks relationship with individual users"""

    user_id: int
    user_name: str = ""

    # Interaction history
    total_interactions: int = 0
    positive_interactions: int = 0
    humor_exchanges: int = 0
    help_provided: int = 0

    # Personal details remembered
    interests: List[str] = field(default_factory=list)
    achievements: List[Dict[str, Any]] = field(default_factory=list)
    important_dates: Dict[str, str] = field(default_factory=dict)  # birthday, etc.
    personal_references: List[str] = field(default_factory=list)

    # Communication preferences learned
    preferred_response_style: str = "balanced"
    humor_receptivity: float = 0.5
    formality_preference: float = 0.5

    # Relationship quality
    relationship_strength: float = 0.1  # 0.0 = stranger, 1.0 = close friend
    trust_level: float = 0.1  # How much personal info they've shared

    last_interaction: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def update_relationship(self, interaction_type: str, positive: bool = True):
        """Update relationship based on interaction"""
        self.total_interactions += 1
        if positive:
            self.positive_interactions += 1

        if interaction_type == "humor":
            self.humor_exchanges += 1
        elif interaction_type == "help":
            self.help_provided += 1

        # Update relationship strength (gradual growth)
        if positive:
            growth = 0.05 * (1.0 - self.relationship_strength)  # Diminishing returns
            self.relationship_strength = min(1.0, self.relationship_strength + growth)

        self.last_interaction = datetime.now(timezone.utc)


class CultureAnalyzer:
    """Analyzes server culture and communication patterns"""

    def __init__(self):
        self.culture_indicators = {
            "humor_frequency": {
                "keywords": ["lol", "haha", "funny", "joke", "😂", "🤣", "😆"],
                "patterns": [r"haha+", r"lol+", r"😂+"],
            },
            "technical_depth": {
                "keywords": [
                    "algorithm",
                    "code",
                    "programming",
                    "technical",
                    "documentation",
                    "implementation",
                ],
                "patterns": [r"\bapi\b", r"\bfunction\b", r"\bclass\b"],
            },
            "social_warmth": {
                "keywords": [
                    "thanks",
                    "appreciate",
                    "love",
                    "awesome",
                    "great job",
                    "well done",
                ],
                "patterns": [r"thank you", r"good job", r"well done"],
            },
            "formality_preference": {
                "formal_indicators": [
                    "please",
                    "thank you",
                    "could you",
                    "would you mind",
                ],
                "casual_indicators": ["hey", "sup", "gonna", "wanna", "yeah", "nah"],
            },
        }

    def analyze_message_culture(self, message: str) -> Dict[str, float]:
        """Analyze cultural indicators in a message"""
        message_lower = message.lower()
        scores = {}

        # Humor frequency
        humor_score = 0.0
        for keyword in self.culture_indicators["humor_frequency"]["keywords"]:
            if keyword in message_lower:
                humor_score += 0.2

        for pattern in self.culture_indicators["humor_frequency"]["patterns"]:
            import re

            if re.search(pattern, message_lower):
                humor_score += 0.3

        scores["humor_frequency"] = min(1.0, humor_score)

        # Technical depth
        tech_score = 0.0
        for keyword in self.culture_indicators["technical_depth"]["keywords"]:
            if keyword in message_lower:
                tech_score += 0.25

        scores["technical_depth"] = min(1.0, tech_score)

        # Social warmth
        warmth_score = 0.0
        for keyword in self.culture_indicators["social_warmth"]["keywords"]:
            if keyword in message_lower:
                warmth_score += 0.3

        scores["social_warmth"] = min(1.0, warmth_score)

        # Formality preference
        formal_score = 0.0
        casual_score = 0.0

        for indicator in self.culture_indicators["formality_preference"][
            "formal_indicators"
        ]:
            if indicator in message_lower:
                formal_score += 0.25

        for indicator in self.culture_indicators["formality_preference"][
            "casual_indicators"
        ]:
            if indicator in message_lower:
                casual_score += 0.25

        # Net formality score (positive = formal, negative = casual)
        scores["formality_preference"] = min(
            1.0, max(0.0, formal_score - casual_score + 0.5)
        )

        return scores

    def extract_emoji_patterns(self, message: str) -> List[str]:
        """Extract emoji usage patterns"""
        import re

        # Find Unicode emojis
        emoji_pattern = re.compile(
            "[\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map symbols
            "\U0001f1e0-\U0001f1ff"  # flags (iOS)
            "\U00002702-\U000027b0"
            "\U000024c2-\U0001f251"
            "]+",
            flags=re.UNICODE,
        )

        return emoji_pattern.findall(message)

    def detect_inside_jokes(self, messages: List[str]) -> List[str]:
        """Detect potential inside jokes or repeated phrases"""
        phrase_counts = defaultdict(int)

        for message in messages:
            words = message.lower().split()
            # Look for repeated phrases (3+ words)
            for i in range(len(words) - 2):
                phrase = " ".join(words[i : i + 3])
                if len(phrase) > 10:  # Only meaningful phrases
                    phrase_counts[phrase] += 1

        # Return phrases mentioned multiple times
        return [phrase for phrase, count in phrase_counts.items() if count >= 3]


class PersonalityEvolutionEngine:
    """Main engine for personality evolution"""

    def __init__(self):
        self.logger = logger
        self.culture_analyzer = CultureAnalyzer()

        # Server personalities
        self.server_personalities: Dict[int, PersonalityProfile] = {}

        # Database setup
        self.db_path = Path("data/personality_evolution.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._setup_database()

        # Evolution parameters
        self.evolution_threshold = 50  # Messages before considering evolution
        self.confidence_growth_rate = 0.02  # How fast we gain confidence
        self.trait_adaptation_rate = 0.05  # How fast traits change

        logger.info("Personality Evolution Engine initialized")

    def _setup_database(self):
        """Setup database for personality tracking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Server personalities
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS server_personalities (
                        server_id INTEGER PRIMARY KEY,
                        server_name TEXT,
                        personality_data TEXT,
                        culture_confidence REAL DEFAULT 0.1,
                        total_interactions INTEGER DEFAULT 0,
                        last_evolution TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # User relationships
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_relationships (
                        server_id INTEGER,
                        user_id INTEGER,
                        user_name TEXT,
                        relationship_data TEXT,
                        relationship_strength REAL DEFAULT 0.1,
                        total_interactions INTEGER DEFAULT 0,
                        last_interaction TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (server_id, user_id)
                    )
                """
                )

                # Culture evolution events
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS culture_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        server_id INTEGER,
                        event_type TEXT,
                        event_data TEXT,
                        impact_score REAL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create indexes
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_server_personalities_server_id ON server_personalities (server_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_user_relationships_server_user ON user_relationships (server_id, user_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_culture_events_server_id ON culture_events (server_id)"
                )

                conn.commit()
                logger.info("Personality evolution database initialized")

        except Exception as e:
            logger.error(f"Database setup error: {e}")

    async def process_message(
        self,
        message_content: str,
        user_id: int,
        user_name: str,
        server_id: int,
        server_name: str,
        message_context: Any = None,
    ) -> Dict[str, Any]:
        """Process a message and evolve personality accordingly"""

        # Get or create server personality
        personality = await self._get_server_personality(server_id, server_name)

        # Get or create user relationship
        relationship = await self._get_user_relationship(server_id, user_id, user_name)

        # Analyze message for cultural indicators
        culture_scores = self.culture_analyzer.analyze_message_culture(message_content)

        # Extract patterns
        emojis = self.culture_analyzer.extract_emoji_patterns(message_content)

        # Update personality based on message
        evolution_changes = await self._evolve_personality(
            personality,
            relationship,
            message_content,
            culture_scores,
            emojis,
            message_context,
        )

        # Update relationship
        await self._update_relationship(relationship, message_content, message_context)

        # Save changes
        await self._save_personality(personality)
        await self._save_relationship(relationship, server_id)

        return {
            "personality_changes": evolution_changes,
            "relationship_update": {
                "strength": relationship.relationship_strength,
                "interactions": relationship.total_interactions,
            },
            "culture_confidence": personality.culture_confidence,
        }

    async def get_personality_context(
        self, server_id: int, user_id: int = None
    ) -> Dict[str, Any]:
        """Get personality context for response generation"""
        personality = await self._get_server_personality(server_id)
        context = {
            "personality_summary": personality.get_personality_summary(),
            "humor_style": personality.humor_style,
            "formality_level": personality.formality_level,
            "social_energy": personality.social_energy,
            "communication_density": personality.communication_density,
            "emotional_style": personality.emotional_style,
            "preferred_emojis": personality.preferred_emojis[-10:],  # Recent emojis
            "inside_jokes": personality.inside_jokes[-5:],  # Recent inside jokes
            "culture_confidence": personality.culture_confidence,
        }

        if user_id:
            relationship = await self._get_user_relationship(server_id, user_id)
            context["user_relationship"] = {
                "strength": relationship.relationship_strength,
                "interests": relationship.interests,
                "preferred_style": relationship.preferred_response_style,
                "humor_receptivity": relationship.humor_receptivity,
                "personal_references": relationship.personal_references[
                    -3:
                ],  # Recent references
            }

        return context

    async def _get_server_personality(
        self, server_id: int, server_name: str = ""
    ) -> PersonalityProfile:
        """Get or create server personality"""
        if server_id in self.server_personalities:
            return self.server_personalities[server_id]

        # Try loading from database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT personality_data, culture_confidence, total_interactions, last_evolution FROM server_personalities WHERE server_id = ?",
                    (server_id,),
                )
                row = cursor.fetchone()

                if row:
                    personality_data = json.loads(row[0])
                    personality = PersonalityProfile(
                        server_id=server_id, **personality_data
                    )
                    personality.culture_confidence = row[1]
                    personality.total_interactions = row[2]
                    if row[3]:
                        personality.last_evolution = datetime.fromisoformat(row[3])
                else:
                    # Create new personality
                    personality = PersonalityProfile(
                        server_id=server_id, server_name=server_name
                    )

        except Exception as e:
            logger.warning(f"Error loading personality for server {server_id}: {e}")
            personality = PersonalityProfile(
                server_id=server_id, server_name=server_name
            )

        self.server_personalities[server_id] = personality
        return personality

    async def _get_user_relationship(
        self, server_id: int, user_id: int, user_name: str = ""
    ) -> UserRelationship:
        """Get or create user relationship"""
        # Try loading from database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT relationship_data, relationship_strength, total_interactions, last_interaction FROM user_relationships WHERE server_id = ? AND user_id = ?",
                    (server_id, user_id),
                )
                row = cursor.fetchone()

                if row:
                    relationship_data = json.loads(row[0])
                    relationship = UserRelationship(
                        user_id=user_id, **relationship_data
                    )
                    relationship.relationship_strength = row[1]
                    relationship.total_interactions = row[2]
                    if row[3]:
                        relationship.last_interaction = datetime.fromisoformat(row[3])
                else:
                    # Create new relationship
                    relationship = UserRelationship(
                        user_id=user_id, user_name=user_name
                    )

        except Exception as e:
            logger.warning(
                f"Error loading relationship for user {user_id} in server {server_id}: {e}"
            )
            relationship = UserRelationship(user_id=user_id, user_name=user_name)

        return relationship

    async def _evolve_personality(
        self,
        personality: PersonalityProfile,
        relationship: UserRelationship,
        message: str,
        culture_scores: Dict[str, float],
        emojis: List[str],
        message_context: Any = None,
    ) -> Dict[str, Any]:
        """Evolve personality based on new interaction"""
        changes = {}

        personality.total_interactions += 1

        # Gradually increase culture confidence
        personality.culture_confidence = min(
            1.0, personality.culture_confidence + self.confidence_growth_rate
        )

        # Adapt formality level
        if "formality_preference" in culture_scores:
            current_formality = personality.formality_level
            target_formality = culture_scores["formality_preference"]
            adaptation = self.trait_adaptation_rate * personality.culture_confidence

            new_formality = (
                current_formality + (target_formality - current_formality) * adaptation
            )
            personality.formality_level = max(0.0, min(1.0, new_formality))

            if abs(new_formality - current_formality) > 0.01:
                changes["formality_level"] = {
                    "old": current_formality,
                    "new": personality.formality_level,
                    "change": new_formality - current_formality,
                }

        # Adapt social energy based on message context
        if message_context and hasattr(message_context, "emotional_intensity"):
            if message_context.emotional_intensity > 0.7:
                # High energy message, gradually increase social energy
                energy_boost = 0.02 * personality.culture_confidence
                old_energy = personality.social_energy
                personality.social_energy = min(
                    1.0, personality.social_energy + energy_boost
                )

                if personality.social_energy != old_energy:
                    changes["social_energy"] = {
                        "old": old_energy,
                        "new": personality.social_energy,
                        "reason": "high_energy_message",
                    }

        # Learn emoji preferences
        for emoji in emojis:
            if emoji not in personality.preferred_emojis:
                personality.preferred_emojis.append(emoji)
            # Keep only last 50 emojis
            if len(personality.preferred_emojis) > 50:
                personality.preferred_emojis = personality.preferred_emojis[-50:]

        # Detect and learn humor style
        if (
            message_context
            and hasattr(message_context, "humor_score")
            and message_context.humor_score > 0.3
        ):
            # This is a humorous message, learn from it
            humor_adaptation = 0.03 * personality.culture_confidence

            # Detect humor type and adapt
            message_lower = message.lower()
            if (
                any(word in message_lower for word in ["pun", "punny"])
                or "😂" in emojis
            ):
                old_value = personality.humor_style["punny"]
                personality.humor_style["punny"] = min(
                    1.0, old_value + humor_adaptation
                )
                if personality.humor_style["punny"] != old_value:
                    changes["humor_style"] = changes.get("humor_style", {})
                    changes["humor_style"]["punny"] = {
                        "old": old_value,
                        "new": personality.humor_style["punny"],
                    }

            if any(word in message_lower for word in ["meme", "dank", "based"]):
                old_value = personality.humor_style["memes"]
                personality.humor_style["memes"] = min(
                    1.0, old_value + humor_adaptation
                )
                if personality.humor_style["memes"] != old_value:
                    changes["humor_style"] = changes.get("humor_style", {})
                    changes["humor_style"]["memes"] = {
                        "old": old_value,
                        "new": personality.humor_style["memes"],
                    }

        # Update last evolution time
        personality.last_evolution = datetime.now(timezone.utc)

        return changes

    async def _update_relationship(
        self, relationship: UserRelationship, message: str, message_context: Any = None
    ):
        """Update user relationship based on interaction"""
        interaction_type = "general"
        positive = True

        if message_context:
            if (
                hasattr(message_context, "humor_score")
                and message_context.humor_score > 0.3
            ):
                interaction_type = "humor"
            elif hasattr(message_context, "response_triggers"):
                if any(
                    "help" in str(trigger)
                    for trigger in message_context.response_triggers
                ):
                    interaction_type = "help"

        # Detect if user shared personal information
        personal_indicators = [
            "my birthday",
            "i work",
            "i study",
            "my job",
            "i live",
            "i love",
            "i hate",
            "my favorite",
        ]
        if any(indicator in message.lower() for indicator in personal_indicators):
            relationship.trust_level = min(1.0, relationship.trust_level + 0.1)

            # Extract and remember personal information (simplified)
            message_lower = message.lower()
            if "birthday" in message_lower:
                relationship.important_dates["birthday_mentioned"] = datetime.now(
                    timezone.utc
                ).isoformat()

            # Add to personal references
            if len(message) > 20:  # Meaningful personal message
                relationship.personal_references.append(message[:100])
                # Keep only last 10 references
                if len(relationship.personal_references) > 10:
                    relationship.personal_references = relationship.personal_references[
                        -10:
                    ]

        relationship.update_relationship(interaction_type, positive)

    async def _save_personality(self, personality: PersonalityProfile):
        """Save personality to database"""
        try:
            personality_data = {
                "server_name": personality.server_name,
                "humor_style": personality.humor_style,
                "formality_level": personality.formality_level,
                "topic_enthusiasm": personality.topic_enthusiasm,
                "social_energy": personality.social_energy,
                "communication_density": personality.communication_density,
                "emotional_style": personality.emotional_style,
                "preferred_emojis": personality.preferred_emojis,
                "inside_jokes": personality.inside_jokes,
                "cultural_references": personality.cultural_references,
                "celebration_phrases": personality.celebration_phrases,
                "support_phrases": personality.support_phrases,
                "user_relationships": personality.user_relationships,
            }

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO server_personalities 
                    (server_id, server_name, personality_data, culture_confidence, total_interactions, last_evolution, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        personality.server_id,
                        personality.server_name,
                        json.dumps(personality_data),
                        personality.culture_confidence,
                        personality.total_interactions,
                        personality.last_evolution.isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"Error saving personality: {e}")

    async def _save_relationship(self, relationship: UserRelationship, server_id: int):
        """Save relationship to database"""
        try:
            relationship_data = {
                "user_name": relationship.user_name,
                "positive_interactions": relationship.positive_interactions,
                "humor_exchanges": relationship.humor_exchanges,
                "help_provided": relationship.help_provided,
                "interests": relationship.interests,
                "achievements": relationship.achievements,
                "important_dates": relationship.important_dates,
                "personal_references": relationship.personal_references,
                "preferred_response_style": relationship.preferred_response_style,
                "humor_receptivity": relationship.humor_receptivity,
                "formality_preference": relationship.formality_preference,
                "trust_level": relationship.trust_level,
            }

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO user_relationships 
                    (server_id, user_id, user_name, relationship_data, relationship_strength, total_interactions, last_interaction, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        server_id,
                        relationship.user_id,
                        relationship.user_name,
                        json.dumps(relationship_data),
                        relationship.relationship_strength,
                        relationship.total_interactions,
                        relationship.last_interaction.isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"Error saving relationship: {e}")

    async def get_analytics(self, server_id: int = None) -> Dict[str, Any]:
        """Get personality evolution analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if server_id:
                    # Server-specific analytics
                    cursor.execute(
                        "SELECT * FROM server_personalities WHERE server_id = ?",
                        (server_id,),
                    )
                    personality_data = cursor.fetchone()

                    cursor.execute(
                        "SELECT COUNT(*), AVG(relationship_strength) FROM user_relationships WHERE server_id = ?",
                        (server_id,),
                    )
                    relationship_stats = cursor.fetchone()

                    return {
                        "server_id": server_id,
                        "has_personality": personality_data is not None,
                        "culture_confidence": (
                            personality_data[3] if personality_data else 0
                        ),
                        "total_interactions": (
                            personality_data[4] if personality_data else 0
                        ),
                        "user_relationships": (
                            relationship_stats[0] if relationship_stats else 0
                        ),
                        "avg_relationship_strength": (
                            relationship_stats[1] if relationship_stats else 0
                        ),
                    }
                else:
                    # Global analytics
                    cursor.execute("SELECT COUNT(*) FROM server_personalities")
                    total_servers = cursor.fetchone()[0]

                    cursor.execute("SELECT COUNT(*) FROM user_relationships")
                    total_relationships = cursor.fetchone()[0]

                    cursor.execute(
                        "SELECT AVG(culture_confidence) FROM server_personalities"
                    )
                    avg_confidence = cursor.fetchone()[0] or 0

                    return {
                        "total_servers_with_personality": total_servers,
                        "total_user_relationships": total_relationships,
                        "average_culture_confidence": avg_confidence,
                    }

        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}


# Global personality engine instance
_personality_engine: Optional[PersonalityEvolutionEngine] = None


def get_personality_engine() -> Optional[PersonalityEvolutionEngine]:
    """Get the global personality engine instance"""
    return _personality_engine


def initialize_personality_engine() -> PersonalityEvolutionEngine:
    """Initialize the global personality engine"""
    global _personality_engine
    _personality_engine = PersonalityEvolutionEngine()
    return _personality_engine
