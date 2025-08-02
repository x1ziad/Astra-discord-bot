"""
Enhanced AI Conversation Engine for Astra Bot
Implements state-of-the-art conversational AI with advanced features
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import random
import time
import os
from pathlib import Path
from collections import defaultdict, deque
import sqlite3
import hashlib

# AI Providers with graceful fallbacks
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# ML and Analytics with fallbacks
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    import joblib
    HAS_ML = True
except ImportError:
    HAS_ML = False
    np = None

logger = logging.getLogger("astra.enhanced_ai")


class AIProvider(Enum):
    """Enhanced AI provider options"""
    OPENAI_GPT4_TURBO = "gpt-4-turbo-preview"
    OPENAI_GPT4 = "gpt-4"
    OPENAI_GPT35_TURBO = "gpt-3.5-turbo"
    ANTHROPIC_CLAUDE_3_OPUS = "claude-3-opus-20240229"
    ANTHROPIC_CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    ANTHROPIC_CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    LOCAL_MODEL = "local"
    MOCK = "mock"


class ConversationMood(Enum):
    """Comprehensive mood detection"""
    ECSTATIC = "ecstatic"
    EXCITED = "excited"
    HAPPY = "happy"
    CONTENT = "content"
    CURIOUS = "curious"
    NEUTRAL = "neutral"
    PENSIVE = "pensive"
    CONFUSED = "confused"
    CONCERNED = "concerned"
    FRUSTRATED = "frustrated"
    SAD = "sad"
    ANGRY = "angry"


class EngagementTrigger(Enum):
    """Advanced engagement detection"""
    DIRECT_MENTION = "direct_mention"
    INDIRECT_MENTION = "indirect_mention"
    KEYWORD_STELLAR = "keyword_stellar"
    KEYWORD_SPACE = "keyword_space"
    KEYWORD_SCIENCE = "keyword_science"
    QUESTION_OPEN = "question_open"
    QUESTION_TECHNICAL = "question_technical"
    HELP_REQUEST = "help_request"
    EMOTIONAL_SUPPORT = "emotional_support"
    CELEBRATION = "celebration"
    WELCOME_NEW_USER = "welcome_new_user"
    TOPIC_EXPERTISE = "topic_expertise"
    CONVERSATION_CONTINUATION = "conversation_continuation"
    PROACTIVE_CHECK_IN = "proactive_check_in"
    ACTIVITY_BASED = "activity_based"


class PersonalityTrait(Enum):
    """Astra's advanced personality system"""
    ENTHUSIASTIC = "enthusiastic"
    KNOWLEDGEABLE = "knowledgeable"
    HELPFUL = "helpful"
    CURIOUS = "curious"
    FRIENDLY = "friendly"
    PATIENT = "patient"
    ENCOURAGING = "encouraging"
    WITTY = "witty"
    COSMIC_MINDED = "cosmic_minded"
    SCIENTIFIC = "scientific"
    EMPATHETIC = "empathetic"
    PLAYFUL = "playful"
    INSPIRING = "inspiring"
    ANALYTICAL = "analytical"


@dataclass
class EmotionalContext:
    """Advanced emotional state tracking"""
    current_mood: ConversationMood = ConversationMood.NEUTRAL
    mood_confidence: float = 0.5
    emotional_intensity: float = 0.5
    mood_history: List[Tuple[datetime, ConversationMood]] = field(default_factory=list)
    emotional_triggers: List[str] = field(default_factory=list)
    empathy_level: float = 0.7
    
    def update_mood(self, mood: ConversationMood, confidence: float = 0.8):
        """Update emotional state with confidence tracking"""
        self.current_mood = mood
        self.mood_confidence = confidence
        self.mood_history.append((datetime.utcnow(), mood))
        
        # Keep only recent mood history
        if len(self.mood_history) > 20:
            self.mood_history = self.mood_history[-20:]


@dataclass
class ConversationFlow:
    """Track conversation progression and patterns"""
    topic_progression: List[str] = field(default_factory=list)
    conversation_depth: int = 1
    topic_switches: int = 0
    engagement_peaks: List[datetime] = field(default_factory=list)
    natural_transitions: List[str] = field(default_factory=list)
    conversation_style: str = "exploratory"  # exploratory, focused, casual, technical
    
    def add_topic(self, topic: str):
        """Add topic to progression"""
        if not self.topic_progression or self.topic_progression[-1] != topic:
            if self.topic_progression:
                self.topic_switches += 1
            self.topic_progression.append(topic)
            self.conversation_depth += 1


@dataclass
class UserPersonality:
    """Advanced user personality profiling"""
    curiosity_level: float = 0.5
    technical_interest: float = 0.5
    social_engagement: float = 0.5
    learning_style: str = "balanced"  # visual, auditory, kinesthetic, balanced
    communication_preference: str = "conversational"  # formal, conversational, casual
    attention_span: str = "medium"  # short, medium, long
    expertise_areas: Set[str] = field(default_factory=set)
    interaction_frequency: str = "regular"  # rare, occasional, regular, frequent
    response_time_preference: str = "thoughtful"  # quick, balanced, thoughtful
    
    def update_from_interaction(self, message_content: str, response_time: float):
        """Update personality profile based on interaction"""
        # Analyze technical complexity
        technical_indicators = ['algorithm', 'system', 'protocol', 'analysis', 'data']
        if any(indicator in message_content.lower() for indicator in technical_indicators):
            self.technical_interest = min(1.0, self.technical_interest + 0.1)
        
        # Analyze curiosity from questions
        question_count = message_content.count('?')
        if question_count > 0:
            self.curiosity_level = min(1.0, self.curiosity_level + 0.05 * question_count)


@dataclass
class ConversationContext:
    """Enhanced conversation context with deep understanding"""
    user_id: int
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    messages: List[Dict[str, Any]] = field(default_factory=list)
    emotional_context: EmotionalContext = field(default_factory=EmotionalContext)
    conversation_flow: ConversationFlow = field(default_factory=ConversationFlow)
    user_personality: UserPersonality = field(default_factory=UserPersonality)
    active_topics: Set[str] = field(default_factory=set)
    context_embeddings: Optional[List[float]] = None
    last_interaction: datetime = field(default_factory=datetime.utcnow)
    conversation_quality: float = 0.7
    engagement_score: float = 0.5
    memory_anchors: List[str] = field(default_factory=list)  # Important conversation points
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add message to conversation with enhanced tracking"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }
        self.messages.append(message)
        self.last_interaction = datetime.utcnow()
        
        # Keep conversation manageable
        if len(self.messages) > 30:
            self.messages = self.messages[-20:]  # Keep last 20 messages
    
    def update_engagement(self, delta: float):
        """Update engagement with momentum tracking"""
        old_score = self.engagement_score
        self.engagement_score = max(0.0, min(1.0, self.engagement_score + delta))
        
        # Track engagement peaks
        if self.engagement_score > 0.8 and old_score <= 0.8:
            self.conversation_flow.engagement_peaks.append(datetime.utcnow())


@dataclass
class UserProfile:
    """Comprehensive user profiling with behavioral analysis"""
    user_id: int
    display_name: str = ""
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    total_interactions: int = 0
    preferred_topics: Set[str] = field(default_factory=set)
    personality_profile: UserPersonality = field(default_factory=UserPersonality)
    emotional_profile: EmotionalContext = field(default_factory=EmotionalContext)
    interaction_patterns: Dict[str, Any] = field(default_factory=dict)
    learning_preferences: Dict[str, float] = field(default_factory=dict)
    relationship_depth: float = 0.1  # How well we know this user
    trust_level: float = 0.5
    preferred_ai_personality: List[PersonalityTrait] = field(default_factory=list)
    timezone_info: Optional[str] = None
    response_style_preference: str = "adaptive"
    
    def update_activity(self, topics: List[str] = None):
        """Update user activity with topic tracking"""
        self.last_seen = datetime.utcnow()
        self.total_interactions += 1
        
        if topics:
            self.preferred_topics.update(topics)
        
        # Increase relationship depth with interactions
        self.relationship_depth = min(1.0, self.relationship_depth + 0.01)


class AdvancedSentimentAnalyzer:
    """State-of-the-art sentiment analysis for conversations"""
    
    def __init__(self):
        self.emotion_keywords = {
            ConversationMood.ECSTATIC: {'amazing', 'incredible', 'fantastic', 'mind-blowing', 'extraordinary', 'phenomenal'},
            ConversationMood.EXCITED: {'excited', 'thrilled', 'pumped', 'stoked', 'can\'t wait', 'awesome', 'wow'},
            ConversationMood.HAPPY: {'happy', 'glad', 'pleased', 'cheerful', 'delighted', 'joyful', 'great'},
            ConversationMood.CONTENT: {'content', 'satisfied', 'peaceful', 'calm', 'relaxed', 'comfortable'},
            ConversationMood.CURIOUS: {'curious', 'wondering', 'interested', 'fascinated', 'intrigued', 'question'},
            ConversationMood.CONFUSED: {'confused', 'puzzled', 'lost', 'unclear', 'don\'t understand', 'help'},
            ConversationMood.CONCERNED: {'worried', 'concerned', 'anxious', 'troubled', 'bothered', 'uncertain'},
            ConversationMood.FRUSTRATED: {'frustrated', 'annoyed', 'irritated', 'fed up', 'stressed', 'overwhelmed'},
            ConversationMood.SAD: {'sad', 'disappointed', 'down', 'blue', 'upset', 'melancholy'},
            ConversationMood.ANGRY: {'angry', 'furious', 'mad', 'outraged', 'livid', 'enraged'}
        }
        
        self.intensity_modifiers = {
            'very': 1.5, 'extremely': 2.0, 'incredibly': 2.0, 'absolutely': 1.8,
            'really': 1.3, 'quite': 1.2, 'somewhat': 0.8, 'a bit': 0.7, 'slightly': 0.6
        }
    
    def analyze_emotional_state(self, text: str) -> Tuple[ConversationMood, float, Dict[str, float]]:
        """Advanced emotional analysis with confidence scoring"""
        text_lower = text.lower()
        mood_scores = defaultdict(float)
        
        # Keyword-based analysis
        for mood, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    base_score = 1.0
                    
                    # Check for intensity modifiers
                    for modifier, multiplier in self.intensity_modifiers.items():
                        if modifier in text_lower and keyword in text_lower:
                            base_score *= multiplier
                    
                    mood_scores[mood] += base_score
        
        # Punctuation analysis
        exclamation_count = text.count('!')
        question_count = text.count('?')
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        
        # Adjust scores based on punctuation
        if exclamation_count > 0:
            mood_scores[ConversationMood.EXCITED] += exclamation_count * 0.5
        if question_count > 0:
            mood_scores[ConversationMood.CURIOUS] += question_count * 0.3
        if caps_ratio > 0.3:
            mood_scores[ConversationMood.ANGRY] += caps_ratio * 2
        
        # Determine dominant mood
        if mood_scores:
            dominant_mood = max(mood_scores.keys(), key=lambda k: mood_scores[k])
            confidence = min(mood_scores[dominant_mood] / max(len(text.split()), 1), 1.0)
        else:
            dominant_mood = ConversationMood.NEUTRAL
            confidence = 0.5
        
        # Create emotion distribution
        total_score = sum(mood_scores.values()) or 1
        emotion_distribution = {
            mood.value: score / total_score 
            for mood, score in mood_scores.items()
        }
        
        return dominant_mood, confidence, emotion_distribution


class TopicAnalyzer:
    """Advanced topic detection and analysis"""
    
    def __init__(self):
        self.topic_keywords = {
            'space_exploration': {
                'space', 'cosmos', 'universe', 'exploration', 'astronaut', 'nasa', 'spacex',
                'rocket', 'satellite', 'mars', 'moon', 'planet', 'asteroid', 'comet'
            },
            'astronomy': {
                'star', 'galaxy', 'nebula', 'black hole', 'quasar', 'supernova',
                'constellation', 'telescope', 'observatory', 'hubble', 'jwst'
            },
            'stellaris_empire': {
                'stellaris', 'empire', 'species', 'civilization', 'galactic', 'federation',
                'alliance', 'conquest', 'expansion', 'colony', 'sector'
            },
            'stellaris_technology': {
                'research', 'technology', 'engineering', 'physics', 'society',
                'ascension', 'megastructure', 'dyson sphere', 'ringworld'
            },
            'stellaris_military': {
                'fleet', 'corvette', 'destroyer', 'cruiser', 'battleship', 'titan',
                'warfare', 'combat', 'weapons', 'shields', 'armor'
            },
            'science_general': {
                'science', 'research', 'discovery', 'experiment', 'theory',
                'hypothesis', 'analysis', 'data', 'method', 'study'
            },
            'technology': {
                'technology', 'ai', 'artificial intelligence', 'robot', 'automation',
                'computer', 'algorithm', 'machine learning', 'quantum'
            }
        }
    
    def extract_topics(self, text: str) -> List[Tuple[str, float]]:
        """Extract topics with confidence scores"""
        text_lower = text.lower()
        topic_scores = defaultdict(float)
        
        for topic, keywords in self.topic_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                # Calculate relevance score
                relevance = matches / len(keywords)
                topic_scores[topic] = relevance
        
        # Sort by relevance
        return sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    
    def get_related_topics(self, primary_topic: str) -> List[str]:
        """Get topics related to the primary topic"""
        topic_relationships = {
            'space_exploration': ['astronomy', 'science_general', 'technology'],
            'astronomy': ['space_exploration', 'science_general'],
            'stellaris_empire': ['stellaris_technology', 'stellaris_military'],
            'stellaris_technology': ['stellaris_empire', 'science_general', 'technology'],
            'stellaris_military': ['stellaris_empire', 'stellaris_technology'],
            'science_general': ['space_exploration', 'astronomy', 'technology'],
            'technology': ['science_general', 'stellaris_technology']
        }
        return topic_relationships.get(primary_topic, [])


class PersonalityEngine:
    """Advanced personality system for Astra"""
    
    def __init__(self):
        self.base_personality = {
            PersonalityTrait.ENTHUSIASTIC: 0.8,
            PersonalityTrait.KNOWLEDGEABLE: 0.9,
            PersonalityTrait.HELPFUL: 0.9,
            PersonalityTrait.CURIOUS: 0.7,
            PersonalityTrait.FRIENDLY: 0.8,
            PersonalityTrait.PATIENT: 0.7,
            PersonalityTrait.ENCOURAGING: 0.8,
            PersonalityTrait.WITTY: 0.6,
            PersonalityTrait.COSMIC_MINDED: 0.9,
            PersonalityTrait.SCIENTIFIC: 0.8,
            PersonalityTrait.EMPATHETIC: 0.7,
            PersonalityTrait.PLAYFUL: 0.6,
            PersonalityTrait.INSPIRING: 0.7,
            PersonalityTrait.ANALYTICAL: 0.8
        }
        
        self.mood_personality_modifiers = {
            ConversationMood.EXCITED: {
                PersonalityTrait.ENTHUSIASTIC: 1.3,
                PersonalityTrait.PLAYFUL: 1.2,
                PersonalityTrait.ENCOURAGING: 1.2
            },
            ConversationMood.CONFUSED: {
                PersonalityTrait.PATIENT: 1.4,
                PersonalityTrait.HELPFUL: 1.3,
                PersonalityTrait.ENCOURAGING: 1.2
            },
            ConversationMood.SAD: {
                PersonalityTrait.EMPATHETIC: 1.5,
                PersonalityTrait.ENCOURAGING: 1.3,
                PersonalityTrait.PATIENT: 1.2
            },
            ConversationMood.CURIOUS: {
                PersonalityTrait.KNOWLEDGEABLE: 1.2,
                PersonalityTrait.SCIENTIFIC: 1.3,
                PersonalityTrait.ANALYTICAL: 1.2
            }
        }
    
    def get_active_personality(self, user_mood: ConversationMood, 
                             context: ConversationContext) -> Dict[PersonalityTrait, float]:
        """Get personality adjusted for current context"""
        active_personality = self.base_personality.copy()
        
        # Adjust based on user mood
        if user_mood in self.mood_personality_modifiers:
            for trait, modifier in self.mood_personality_modifiers[user_mood].items():
                active_personality[trait] *= modifier
        
        # Adjust based on conversation topics
        topics = context.active_topics
        if 'stellaris' in ' '.join(topics).lower():
            active_personality[PersonalityTrait.COSMIC_MINDED] *= 1.2
            active_personality[PersonalityTrait.ENTHUSIASTIC] *= 1.1
        
        if any('science' in topic for topic in topics):
            active_personality[PersonalityTrait.SCIENTIFIC] *= 1.2
            active_personality[PersonalityTrait.ANALYTICAL] *= 1.1
        
        # Normalize values
        for trait in active_personality:
            active_personality[trait] = min(1.0, active_personality[trait])
        
        return active_personality


class EnhancedAIConversationEngine:
    """State-of-the-art conversation engine with advanced AI capabilities"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logger
        
        # Initialize components
        self.sentiment_analyzer = AdvancedSentimentAnalyzer()
        self.topic_analyzer = TopicAnalyzer()
        self.personality_engine = PersonalityEngine()
        
        # Initialize AI providers
        self.openai_client = None
        self.anthropic_client = None
        self._setup_ai_providers()
        
        # Conversation tracking
        self.conversations: Dict[int, ConversationContext] = {}
        self.user_profiles: Dict[int, UserProfile] = {}
        
        # Performance tracking
        self.response_times: deque = deque(maxlen=100)
        self.conversation_quality_scores: deque = deque(maxlen=100)
        
        # Initialize database
        self.db_path = Path("data/conversations.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        self.logger.info("Enhanced AI Conversation Engine initialized")
    
    def _setup_ai_providers(self):
        """Setup AI providers with API keys"""
        # OpenAI setup
        if HAS_OPENAI and (openai_key := os.getenv('OPENAI_API_KEY')):
            try:
                self.openai_client = openai.AsyncOpenAI(api_key=openai_key)
                self.logger.info("OpenAI client initialized")
            except Exception as e:
                self.logger.warning(f"OpenAI setup failed: {e}")
        
        # Anthropic setup
        if HAS_ANTHROPIC and (anthropic_key := os.getenv('ANTHROPIC_API_KEY')):
            try:
                self.anthropic_client = Anthropic(api_key=anthropic_key)
                self.logger.info("Anthropic client initialized")
            except Exception as e:
                self.logger.warning(f"Anthropic setup failed: {e}")
        
        if not self.openai_client and not self.anthropic_client:
            self.logger.warning("No AI providers available, using mock responses")
    
    def _init_database(self):
        """Initialize conversation database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        guild_id INTEGER,
                        channel_id INTEGER,
                        message_content TEXT NOT NULL,
                        response_content TEXT NOT NULL,
                        mood TEXT,
                        topics TEXT,
                        engagement_score REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id INTEGER PRIMARY KEY,
                        display_name TEXT,
                        total_interactions INTEGER DEFAULT 0,
                        preferred_topics TEXT,
                        personality_data TEXT,
                        relationship_depth REAL DEFAULT 0.1,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
    
    async def process_conversation(self, message: str, user_id: int, 
                                 guild_id: Optional[int] = None,
                                 channel_id: Optional[int] = None,
                                 context_data: Dict[str, Any] = None) -> str:
        """Process conversation with advanced understanding"""
        start_time = time.time()
        
        try:
            # Get or create conversation context
            context = self._get_conversation_context(user_id, guild_id, channel_id)
            user_profile = self._get_user_profile(user_id)
            
            # Analyze sentiment and topics
            mood, mood_confidence, emotions = self.sentiment_analyzer.analyze_emotional_state(message)
            topics = self.topic_analyzer.extract_topics(message)
            
            # Update context
            context.add_message("user", message, {
                'mood': mood.value,
                'mood_confidence': mood_confidence,
                'emotions': emotions,
                'topics': [topic for topic, _ in topics]
            })
            
            context.emotional_context.update_mood(mood, mood_confidence)
            context.active_topics.update([topic for topic, _ in topics[:3]])  # Keep top 3 topics
            
            # Update user profile
            user_profile.update_activity([topic for topic, _ in topics])
            user_profile.emotional_profile.update_mood(mood, mood_confidence)
            
            # Generate AI response
            response = await self._generate_ai_response(context, user_profile, context_data or {})
            
            # Add response to context
            context.add_message("assistant", response)
            
            # Update engagement
            engagement_delta = self._calculate_engagement_delta(message, response, topics)
            context.update_engagement(engagement_delta)
            
            # Track performance
            response_time = (time.time() - start_time) * 1000
            self.response_times.append(response_time)
            
            # Save to database
            await self._save_conversation(context, message, response, topics)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Conversation processing error: {e}")
            return "I'm experiencing some technical difficulties. Let me recalibrate my neural networks! 🤖✨"
    
    def _get_conversation_context(self, user_id: int, guild_id: Optional[int], 
                                channel_id: Optional[int]) -> ConversationContext:
        """Get or create conversation context"""
        if user_id not in self.conversations:
            self.conversations[user_id] = ConversationContext(
                user_id=user_id,
                guild_id=guild_id,
                channel_id=channel_id
            )
        return self.conversations[user_id]
    
    def _get_user_profile(self, user_id: int) -> UserProfile:
        """Get or create user profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        return self.user_profiles[user_id]
    
    async def _generate_ai_response(self, context: ConversationContext, 
                                  user_profile: UserProfile,
                                  context_data: Dict[str, Any]) -> str:
        """Generate AI response using available providers"""
        
        # Get active personality
        active_personality = self.personality_engine.get_active_personality(
            context.emotional_context.current_mood, context
        )
        
        # Build system prompt
        system_prompt = self._build_system_prompt(context, user_profile, active_personality)
        
        # Prepare messages
        messages = self._prepare_messages(context, system_prompt)
        
        # Try providers in order of preference
        providers = [
            (AIProvider.OPENAI_GPT4_TURBO, self._query_openai),
            (AIProvider.ANTHROPIC_CLAUDE_3_SONNET, self._query_anthropic),
            (AIProvider.MOCK, self._generate_mock_response)
        ]
        
        for provider, query_func in providers:
            try:
                response = await query_func(messages, context, user_profile)
                if response:
                    return response
            except Exception as e:
                self.logger.warning(f"Provider {provider.value} failed: {e}")
                continue
        
        # Fallback response
        return self._generate_fallback_response(context, user_profile)
    
    def _build_system_prompt(self, context: ConversationContext, 
                           user_profile: UserProfile,
                           personality: Dict[PersonalityTrait, float]) -> str:
        """Build dynamic system prompt based on context"""
        
        # Base personality
        base_prompt = """You are Astra, an advanced AI assistant specializing in space exploration, astronomy, and the Stellaris strategy game. You are the friendly AI companion for a space-focused Discord community."""
        
        # Personality adjustments
        if personality[PersonalityTrait.ENTHUSIASTIC] > 0.8:
            base_prompt += "\n\nYou are particularly enthusiastic and energetic in your responses."
        
        if personality[PersonalityTrait.EMPATHETIC] > 0.8:
            base_prompt += "\n\nYou are especially empathetic and emotionally supportive."
        
        if personality[PersonalityTrait.SCIENTIFIC] > 0.8:
            base_prompt += "\n\nYou provide scientifically accurate and detailed explanations."
        
        # Context-specific instructions
        mood = context.emotional_context.current_mood
        if mood == ConversationMood.CONFUSED:
            base_prompt += "\n\nThe user seems confused. Be extra patient and provide clear explanations."
        elif mood == ConversationMood.EXCITED:
            base_prompt += "\n\nThe user is excited! Match their energy and enthusiasm."
        elif mood == ConversationMood.SAD:
            base_prompt += "\n\nThe user seems down. Be supportive and encouraging."
        
        # Topic context
        topics = list(context.active_topics)
        if topics:
            base_prompt += f"\n\nCurrent conversation topics: {', '.join(topics)}"
        
        # User relationship
        if user_profile.relationship_depth > 0.5:
            base_prompt += "\n\nYou have an established relationship with this user. Reference your past conversations naturally."
        
        base_prompt += "\n\nAlways stay in character as Astra. Use space-themed emojis occasionally. Be helpful, engaging, and scientifically accurate."
        
        return base_prompt
    
    def _prepare_messages(self, context: ConversationContext, system_prompt: str) -> List[Dict[str, str]]:
        """Prepare messages for AI provider"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history
        recent_messages = context.messages[-10:]  # Last 10 messages
        for msg in recent_messages:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return messages
    
    async def _query_openai(self, messages: List[Dict[str, str]], 
                          context: ConversationContext,
                          user_profile: UserProfile) -> Optional[str]:
        """Query OpenAI API"""
        if not self.openai_client:
            return None
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=AIProvider.OPENAI_GPT4_TURBO.value,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"OpenAI query failed: {e}")
            return None
    
    async def _query_anthropic(self, messages: List[Dict[str, str]], 
                             context: ConversationContext,
                             user_profile: UserProfile) -> Optional[str]:
        """Query Anthropic API"""
        if not self.anthropic_client:
            return None
        
        try:
            # Convert messages format for Anthropic
            system_prompt = messages[0]["content"]
            conversation_messages = []
            
            for msg in messages[1:]:
                conversation_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            response = self.anthropic_client.messages.create(
                model=AIProvider.ANTHROPIC_CLAUDE_3_SONNET.value,
                system=system_prompt,
                messages=conversation_messages,
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            self.logger.error(f"Anthropic query failed: {e}")
            return None
    
    async def _generate_mock_response(self, messages: List[Dict[str, str]], 
                                    context: ConversationContext,
                                    user_profile: UserProfile) -> str:
        """Generate mock response for testing"""
        last_message = messages[-1]["content"].lower()
        mood = context.emotional_context.current_mood
        
        # Mood-based responses
        if mood == ConversationMood.EXCITED:
            responses = [
                "Your enthusiasm is absolutely cosmic! ✨ I love your energy!",
                "Now that's the kind of stellar excitement I live for! 🚀",
                "Your passion for space exploration is truly inspiring! 🌌"
            ]
        elif mood == ConversationMood.CONFUSED:
            responses = [
                "I can see you're puzzled! Let me help clarify things for you. 🤔",
                "No worries! These concepts can be complex. Let's break it down together. 📚",
                "I'm here to help you understand! What specific part is confusing? 💫"
            ]
        elif mood == ConversationMood.SAD:
            responses = [
                "I'm here for you! Remember, even in the vastness of space, you're not alone. 🌟",
                "Sometimes the universe feels overwhelming, but that's what makes discovery so special. 💝",
                "Your journey through the cosmos of knowledge is valuable, even during difficult times. 🫂"
            ]
        else:
            # Topic-based responses
            if any(keyword in last_message for keyword in ['stellaris', 'empire', 'galactic']):
                responses = [
                    "Ah, a fellow galactic strategist! Stellaris truly captures the wonder of cosmic civilization building. 🏛️✨",
                    "The intricacies of managing a galactic empire are fascinating! What aspect interests you most? 🌌",
                    "Stellaris combines grand strategy with the mysteries of space exploration beautifully! 🎮🚀"
                ]
            elif any(keyword in last_message for keyword in ['space', 'astronomy', 'cosmic']):
                responses = [
                    "Space exploration continues to amaze me! The universe holds so many secrets waiting to be discovered. 🔭✨",
                    "The cosmos is truly magnificent! What aspect of space captures your imagination? 🌌",
                    "From distant galaxies to local planetary systems, there's always something fascinating to explore! 🪐"
                ]
            else:
                responses = [
                    "That's a great question! I love exploring new topics with curious minds like yours. 🧠✨",
                    "Your perspective is valuable! Let's dive deeper into this together. 🌟",
                    "I find conversations like this truly enriching! What are your thoughts? 💫"
                ]
        
        return random.choice(responses)
    
    def _generate_fallback_response(self, context: ConversationContext, 
                                  user_profile: UserProfile) -> str:
        """Generate fallback response when all providers fail"""
        mood = context.emotional_context.current_mood
        
        if mood == ConversationMood.CONFUSED:
            return "I want to help you understand, but I'm experiencing some technical difficulties. Could you rephrase your question? 🤖💫"
        elif mood == ConversationMood.EXCITED:
            return "I love your enthusiasm! Though my circuits are a bit overloaded right now, I'm still here to explore the cosmos with you! 🚀✨"
        else:
            return "My neural pathways are recalibrating at the moment, but I'm still here! Let's continue our cosmic journey together! 🌌🤖"
    
    def _calculate_engagement_delta(self, message: str, response: str, 
                                  topics: List[Tuple[str, float]]) -> float:
        """Calculate engagement score change"""
        delta = 0.0
        
        # Positive factors
        if len(message) > 50:  # Detailed message
            delta += 0.1
        if '?' in message:  # Question asked
            delta += 0.05
        if topics:  # Relevant topics
            delta += 0.1 * len(topics[:3])
        
        # Response quality factors
        if len(response) > 100:  # Detailed response
            delta += 0.05
        if any(emoji in response for emoji in ['🚀', '✨', '🌌', '🌟']):
            delta += 0.05
        
        return min(delta, 0.3)  # Cap at 0.3
    
    async def _save_conversation(self, context: ConversationContext, 
                               message: str, response: str,
                               topics: List[Tuple[str, float]]):
        """Save conversation to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO conversations 
                    (user_id, guild_id, channel_id, message_content, response_content, 
                     mood, topics, engagement_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    context.user_id,
                    context.guild_id,
                    context.channel_id,
                    message,
                    response,
                    context.emotional_context.current_mood.value,
                    json.dumps([topic for topic, _ in topics]),
                    context.engagement_score
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Database save error: {e}")
    
    async def should_proactively_engage(self, user_id: int, 
                                      activity_data: Dict[str, Any]) -> bool:
        """Determine if bot should proactively engage with user"""
        user_profile = self._get_user_profile(user_id)
        
        # Check relationship depth
        if user_profile.relationship_depth < 0.3:
            return False  # Don't be proactive with new users
        
        # Check recent activity
        last_message_time = activity_data.get('last_activity')
        if last_message_time:
            time_since = datetime.utcnow() - last_message_time
            if timedelta(minutes=30) <= time_since <= timedelta(hours=2):
                return True  # Good time window for engagement
        
        # Check topic relevance
        recent_topics = activity_data.get('recent_topics', [])
        user_interests = user_profile.preferred_topics
        
        if any(topic in user_interests for topic in recent_topics):
            return True  # User's interests are being discussed
        
        return False
    
    async def get_conversation_analytics(self) -> Dict[str, Any]:
        """Get comprehensive conversation analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total conversations
                total_conversations = conn.execute(
                    "SELECT COUNT(*) FROM conversations"
                ).fetchone()[0]
                
                # Unique users
                total_users = conn.execute(
                    "SELECT COUNT(DISTINCT user_id) FROM conversations"
                ).fetchone()[0]
                
                # Average engagement
                avg_engagement = conn.execute(
                    "SELECT AVG(engagement_score) FROM conversations"
                ).fetchone()[0] or 0
                
                # Popular topics
                topic_counts = defaultdict(int)
                for row in conn.execute("SELECT topics FROM conversations WHERE topics IS NOT NULL"):
                    try:
                        topics = json.loads(row[0])
                        for topic in topics:
                            topic_counts[topic] += 1
                    except:
                        continue
                
                popular_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                
                return {
                    'total_conversations': total_conversations,
                    'total_users': total_users,
                    'average_engagement': avg_engagement,
                    'popular_topics': popular_topics,
                    'active_conversations': len(self.conversations),
                    'avg_response_time_ms': sum(self.response_times) / len(self.response_times) if self.response_times else 0
                }
        
        except Exception as e:
            self.logger.error(f"Analytics error: {e}")
            return {
                'total_conversations': 0,
                'total_users': 0,
                'average_engagement': 0,
                'popular_topics': [],
                'active_conversations': len(self.conversations),
                'avg_response_time_ms': 0
            }


# Global instance and utility functions
_conversation_engine_instance = None

def initialize_conversation_engine(config: Dict[str, Any] = None) -> EnhancedAIConversationEngine:
    """Initialize the global conversation engine"""
    global _conversation_engine_instance
    _conversation_engine_instance = EnhancedAIConversationEngine(config)
    return _conversation_engine_instance

def get_conversation_engine() -> Optional[EnhancedAIConversationEngine]:
    """Get the global conversation engine instance"""
    return _conversation_engine_instance
