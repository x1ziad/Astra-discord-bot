"""
Emotional Soundtrack System
Adapts music based on community mood and conversation tone
"""

import asyncio
import json
import logging
import sqlite3
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid

from ai.consolidated_ai_engine import get_engine


class MoodType(Enum):
    """Types of emotional moods"""

    JOYFUL = "joyful"
    CALM = "calm"
    ENERGETIC = "energetic"
    MELANCHOLIC = "melancholic"
    ANGRY = "angry"
    PEACEFUL = "peaceful"
    EXCITED = "excited"
    REFLECTIVE = "reflective"
    ROMANTIC = "romantic"
    MYSTERIOUS = "mysterious"


class MusicGenre(Enum):
    """Music genres for different moods"""

    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    ROCK = "rock"
    JAZZ = "jazz"
    AMBIENT = "ambient"
    POP = "pop"
    FOLK = "folk"
    HIP_HOP = "hip_hop"
    ORCHESTRAL = "orchestral"
    LO_FI = "lo_fi"


class TrackSource(Enum):
    """Sources for music tracks"""

    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    LOCAL = "local"
    URL = "url"


@dataclass
class MusicTrack:
    """A music track with mood associations"""

    id: str
    title: str
    artist: str
    source: TrackSource
    source_url: str
    duration: int  # seconds
    mood_associations: Dict[MoodType, float] = field(
        default_factory=dict
    )  # mood -> confidence score
    genre: MusicGenre = MusicGenre.AMBIENT
    energy_level: float = 0.5  # 0.0 (very calm) to 1.0 (very energetic)
    valence: float = 0.5  # 0.0 (negative) to 1.0 (positive)
    danceability: float = 0.5  # 0.0 to 1.0
    play_count: int = 0
    last_played: Optional[datetime] = None
    added_by: Optional[int] = None
    added_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def get_mood_score(self, mood: MoodType) -> float:
        """Get the association score for a specific mood"""
        return self.mood_associations.get(mood, 0.0)

    def get_best_mood_match(self) -> Tuple[MoodType, float]:
        """Get the mood this track best matches"""
        if not self.mood_associations:
            return MoodType.CALM, 0.0

        best_mood = max(self.mood_associations.items(), key=lambda x: x[1])
        return best_mood

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "source": self.source.value,
            "source_url": self.source_url,
            "duration": self.duration,
            "mood_associations": {
                k.value: v for k, v in self.mood_associations.items()
            },
            "genre": self.genre.value,
            "energy_level": self.energy_level,
            "valence": self.valence,
            "danceability": self.danceability,
            "play_count": self.play_count,
            "last_played": self.last_played.isoformat() if self.last_played else None,
            "added_by": self.added_by,
            "added_at": self.added_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MusicTrack":
        track = cls(
            id=data["id"],
            title=data["title"],
            artist=data["artist"],
            source=TrackSource(data["source"]),
            source_url=data["source_url"],
            duration=data["duration"],
            genre=MusicGenre(data.get("genre", "ambient")),
            energy_level=data.get("energy_level", 0.5),
            valence=data.get("valence", 0.5),
            danceability=data.get("danceability", 0.5),
            play_count=data.get("play_count", 0),
            last_played=(
                datetime.fromisoformat(data["last_played"])
                if data.get("last_played")
                else None
            ),
            added_by=data.get("added_by"),
            added_at=datetime.fromisoformat(data["added_at"]),
        )

        # Load mood associations
        for mood_str, score in data.get("mood_associations", {}).items():
            track.mood_associations[MoodType(mood_str)] = score

        return track


@dataclass
class MoodSnapshot:
    """A snapshot of community mood at a point in time"""

    id: str
    server_id: int
    channel_id: Optional[int]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    mood_scores: Dict[MoodType, float] = field(default_factory=dict)
    dominant_mood: Optional[MoodType] = None
    sentiment_score: float = 0.0  # -1.0 to 1.0
    energy_level: float = 0.5
    conversation_topics: List[str] = field(default_factory=list)
    active_users: int = 0
    message_count: int = 0

    def get_dominant_mood(self) -> Tuple[MoodType, float]:
        """Get the dominant mood and its score"""
        if not self.mood_scores:
            return MoodType.CALM, 0.0

        dominant = max(self.mood_scores.items(), key=lambda x: x[1])
        return dominant

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "server_id": self.server_id,
            "channel_id": self.channel_id,
            "timestamp": self.timestamp.isoformat(),
            "mood_scores": {k.value: v for k, v in self.mood_scores.items()},
            "dominant_mood": self.dominant_mood.value if self.dominant_mood else None,
            "sentiment_score": self.sentiment_score,
            "energy_level": self.energy_level,
            "conversation_topics": self.conversation_topics,
            "active_users": self.active_users,
            "message_count": self.message_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MoodSnapshot":
        snapshot = cls(
            id=data["id"],
            server_id=data["server_id"],
            channel_id=data.get("channel_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            sentiment_score=data.get("sentiment_score", 0.0),
            energy_level=data.get("energy_level", 0.5),
            conversation_topics=data.get("conversation_topics", []),
            active_users=data.get("active_users", 0),
            message_count=data.get("message_count", 0),
        )

        # Load mood scores
        for mood_str, score in data.get("mood_scores", {}).items():
            snapshot.mood_scores[MoodType(mood_str)] = score

        # Set dominant mood
        if data.get("dominant_mood"):
            snapshot.dominant_mood = MoodType(data["dominant_mood"])

        return snapshot


@dataclass
class SoundtrackSession:
    """An active soundtrack session in a voice channel"""

    id: str
    server_id: int
    channel_id: int
    started_by: int
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    current_mood: MoodType = MoodType.CALM
    current_track: Optional[MusicTrack] = None
    track_started_at: Optional[datetime] = None
    is_playing: bool = False
    volume: float = 0.5
    auto_mode: bool = True
    mood_history: List[MoodSnapshot] = field(default_factory=list)
    user_preferences: Dict[int, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "server_id": self.server_id,
            "channel_id": self.channel_id,
            "started_by": self.started_by,
            "started_at": self.started_at.isoformat(),
            "current_mood": self.current_mood.value,
            "current_track": (
                self.current_track.to_dict() if self.current_track else None
            ),
            "track_started_at": (
                self.track_started_at.isoformat() if self.track_started_at else None
            ),
            "is_playing": self.is_playing,
            "volume": self.volume,
            "auto_mode": self.auto_mode,
            "mood_history": [
                m.to_dict() for m in self.mood_history[-10:]
            ],  # Keep last 10
            "user_preferences": self.user_preferences,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SoundtrackSession":
        session = cls(
            id=data["id"],
            server_id=data["server_id"],
            channel_id=data["channel_id"],
            started_by=data["started_by"],
            started_at=datetime.fromisoformat(data["started_at"]),
            current_mood=MoodType(data.get("current_mood", "calm")),
            track_started_at=(
                datetime.fromisoformat(data["track_started_at"])
                if data.get("track_started_at")
                else None
            ),
            is_playing=data.get("is_playing", False),
            volume=data.get("volume", 0.5),
            auto_mode=data.get("auto_mode", True),
            user_preferences=data.get("user_preferences", {}),
        )

        # Load current track
        if data.get("current_track"):
            session.current_track = MusicTrack.from_dict(data["current_track"])

        # Load mood history
        for mood_data in data.get("mood_history", []):
            session.mood_history.append(MoodSnapshot.from_dict(mood_data))

        return session


class EmotionalSoundtrackSystem:
    """Main system for emotional soundtrack adaptation"""

    def __init__(self, db_path: str = "data/emotional_soundtrack.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("astra.emotional_soundtrack")
        self.ai_engine = get_engine()
        self.active_sessions: Dict[int, SoundtrackSession] = {}  # channel_id -> session
        self.mood_analysis_cache: Dict[str, Dict[str, Any]] = (
            {}
        )  # Cache recent mood analyses

        self._init_database()
        self._load_active_sessions()

    def _init_database(self):
        """Initialize the database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Music tracks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS music_tracks (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Mood snapshots table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS mood_snapshots (
                    id TEXT PRIMARY KEY,
                    server_id INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Active sessions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS active_sessions (
                    channel_id INTEGER PRIMARY KEY,
                    data TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # User preferences table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER NOT NULL,
                    server_id INTEGER NOT NULL,
                    preferences TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, server_id)
                )
            """
            )

            # Track play history
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS track_history (
                    id TEXT PRIMARY KEY,
                    track_id TEXT NOT NULL,
                    channel_id INTEGER NOT NULL,
                    mood TEXT NOT NULL,
                    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()

    def _load_active_sessions(self):
        """Load active sessions from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data FROM active_sessions")
                rows = cursor.fetchall()

                for row in rows:
                    data = json.loads(row[0])
                    session = SoundtrackSession.from_dict(data)
                    self.active_sessions[session.channel_id] = session

                self.logger.info(
                    f"Loaded {len(self.active_sessions)} active soundtrack sessions"
                )

        except Exception as e:
            self.logger.error(f"Error loading active sessions: {e}")

    async def analyze_conversation_mood(
        self,
        server_id: int,
        channel_id: int,
        messages: List[Dict[str, Any]],
        context_window: timedelta = timedelta(minutes=10),
    ) -> MoodSnapshot:
        """Analyze the mood of recent conversation"""
        try:
            if not messages:
                # Return neutral mood snapshot
                snapshot = MoodSnapshot(
                    id=str(uuid.uuid4()),
                    server_id=server_id,
                    channel_id=channel_id,
                    mood_scores={MoodType.CALM: 0.5},
                    dominant_mood=MoodType.CALM,
                    sentiment_score=0.0,
                    energy_level=0.5,
                    active_users=len(set(m.get("author_id") for m in messages)),
                    message_count=len(messages),
                )
                return snapshot

            # Extract message content
            message_texts = []
            for msg in messages:
                content = msg.get("content", "")
                if content.strip():
                    message_texts.append(content)

            if not message_texts:
                return MoodSnapshot(
                    id=str(uuid.uuid4()),
                    server_id=server_id,
                    channel_id=channel_id,
                    mood_scores={MoodType.CALM: 0.5},
                    dominant_mood=MoodType.CALM,
                )

            # Use AI engine to analyze mood
            combined_text = " ".join(message_texts[-20:])  # Last 20 messages

            if self.ai_engine:
                mood_analysis = await self.ai_engine.analyze_emotional_context(
                    text=combined_text, context_type="conversation", server_id=server_id
                )

                if mood_analysis and mood_analysis.get("success"):
                    analysis_data = mood_analysis.get("analysis", {})

                    # Create mood scores
                    mood_scores = {}
                    for mood in MoodType:
                        score = analysis_data.get(f"{mood.value}_score", 0.0)
                        if score > 0.1:  # Only include moods with meaningful scores
                            mood_scores[mood] = score

                    if not mood_scores:
                        mood_scores[MoodType.CALM] = 0.5

                    # Determine dominant mood
                    dominant_mood, _ = max(mood_scores.items(), key=lambda x: x[1])

                    snapshot = MoodSnapshot(
                        id=str(uuid.uuid4()),
                        server_id=server_id,
                        channel_id=channel_id,
                        mood_scores=mood_scores,
                        dominant_mood=dominant_mood,
                        sentiment_score=analysis_data.get("sentiment_score", 0.0),
                        energy_level=analysis_data.get("energy_level", 0.5),
                        conversation_topics=analysis_data.get("topics", []),
                        active_users=len(set(m.get("author_id") for m in messages)),
                        message_count=len(messages),
                    )

                    # Cache the analysis
                    cache_key = (
                        f"{server_id}_{channel_id}_{messages[-1].get('timestamp', '')}"
                    )
                    self.mood_analysis_cache[cache_key] = {
                        "snapshot": snapshot,
                        "expires": datetime.now(timezone.utc) + timedelta(minutes=5),
                    }

                    # Clean old cache entries
                    self._clean_mood_cache()

                    return snapshot

            # Fallback: simple keyword-based analysis
            return await self._fallback_mood_analysis(
                server_id, channel_id, message_texts
            )

        except Exception as e:
            self.logger.error(f"Error analyzing conversation mood: {e}")
            # Return neutral mood
            return MoodSnapshot(
                id=str(uuid.uuid4()),
                server_id=server_id,
                channel_id=channel_id,
                mood_scores={MoodType.CALM: 0.5},
                dominant_mood=MoodType.CALM,
            )

    async def analyze_mood(self, text: str, server_id: int) -> Dict[str, Any]:
        """Analyze mood from text - simplified interface for testing"""
        try:
            # Create a mock message list
            messages = [
                {
                    "content": text,
                    "author_id": 123456789,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ]

            snapshot = await self.analyze_conversation_mood(server_id, 0, messages)

            return {
                "dominant_mood": snapshot.dominant_mood.value,
                "mood_scores": {
                    mood.value: score for mood, score in snapshot.mood_scores.items()
                },
                "sentiment_score": snapshot.sentiment_score,
                "energy_level": snapshot.energy_level,
            }
        except Exception as e:
            self.logger.error(f"Error in analyze_mood: {e}")
            return {
                "dominant_mood": "calm",
                "mood_scores": {"calm": 0.5},
                "sentiment_score": 0.0,
                "energy_level": 0.5,
            }

    async def _fallback_mood_analysis(
        self, server_id: int, channel_id: int, message_texts: List[str]
    ) -> MoodSnapshot:
        """Fallback mood analysis using keyword matching"""
        # Simple keyword-based mood detection
        mood_keywords = {
            MoodType.JOYFUL: [
                "happy",
                "excited",
                "awesome",
                "great",
                "love",
                "wonderful",
                "amazing",
                "😊",
                "😂",
                "🎉",
            ],
            MoodType.CALM: ["relaxed", "peaceful", "calm", "chill", "quiet", "serene"],
            MoodType.ENERGETIC: [
                "energy",
                "pump",
                "hype",
                "excited",
                "motivated",
                "active",
                "🔥",
                "💪",
            ],
            MoodType.MELANCHOLIC: [
                "sad",
                "depressed",
                "lonely",
                "miss",
                "sorry",
                "unfortunate",
                "😢",
                "😔",
            ],
            MoodType.ANGRY: [
                "angry",
                "mad",
                "frustrated",
                "annoyed",
                "hate",
                "terrible",
                "😠",
                "😡",
            ],
            MoodType.PEACEFUL: ["peace", "tranquil", "meditative", "zen", "harmony"],
            MoodType.EXCITED: ["excited", "thrilled", "pumped", "stoked", "can't wait"],
            MoodType.REFLECTIVE: [
                "think",
                "consider",
                "reflect",
                "philosophical",
                "deep",
                "meaning",
            ],
            MoodType.ROMANTIC: [
                "love",
                "romantic",
                "beautiful",
                "sweet",
                "heart",
                "💕",
                "💖",
            ],
            MoodType.MYSTERIOUS: [
                "mystery",
                "secret",
                "unknown",
                "curious",
                "intriguing",
                "enigma",
            ],
        }

        combined_text = " ".join(message_texts).lower()
        mood_scores = {}

        for mood, keywords in mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in combined_text)
            if score > 0:
                mood_scores[mood] = min(score / len(keywords), 1.0)  # Normalize

        if not mood_scores:
            mood_scores[MoodType.CALM] = 0.5

        dominant_mood, _ = max(mood_scores.items(), key=lambda x: x[1])

        return MoodSnapshot(
            id=str(uuid.uuid4()),
            server_id=server_id,
            channel_id=channel_id,
            mood_scores=mood_scores,
            dominant_mood=dominant_mood,
            sentiment_score=(
                sum(mood_scores.values()) / len(mood_scores) if mood_scores else 0.0
            ),
            energy_level=0.5,  # Default
            active_users=len(message_texts),  # Rough estimate
            message_count=len(message_texts),
        )

    def _clean_mood_cache(self):
        """Clean expired mood analysis cache entries"""
        now = datetime.now(timezone.utc)
        expired_keys = [
            key
            for key, data in self.mood_analysis_cache.items()
            if data["expires"] < now
        ]

        for key in expired_keys:
            del self.mood_analysis_cache[key]

    async def select_track_for_mood(
        self,
        mood: MoodType,
        server_id: int,
        exclude_recent: bool = True,
        min_score: float = 0.3,
    ) -> Optional[MusicTrack]:
        """Select an appropriate track for the given mood"""
        try:
            # Get all tracks
            tracks = await self.get_all_tracks()

            if not tracks:
                return None

            # Filter tracks by mood score
            suitable_tracks = []
            for track in tracks:
                mood_score = track.get_mood_score(mood)
                if mood_score >= min_score:
                    suitable_tracks.append((track, mood_score))

            if not suitable_tracks:
                # Try with lower threshold
                suitable_tracks = [
                    (track, track.get_mood_score(mood)) for track in tracks
                ]
                suitable_tracks.sort(key=lambda x: x[1], reverse=True)
                suitable_tracks = suitable_tracks[:10]  # Top 10

            if not suitable_tracks:
                return None

            # Exclude recently played tracks if requested
            if exclude_recent:
                recent_track_ids = await self._get_recently_played_tracks(
                    server_id, hours=2
                )
                suitable_tracks = [
                    (track, score)
                    for track, score in suitable_tracks
                    if track.id not in recent_track_ids
                ]

            if not suitable_tracks:
                return None

            # Select track based on score and some randomness
            # Weight by score but add some variety
            total_score = sum(score for _, score in suitable_tracks)
            if total_score > 0:
                # Weighted random selection
                rand_val = random.uniform(0, total_score)
                cumulative = 0
                for track, score in suitable_tracks:
                    cumulative += score
                    if rand_val <= cumulative:
                        return track

            # Fallback: random selection
            return random.choice([track for track, _ in suitable_tracks])

        except Exception as e:
            self.logger.error(f"Error selecting track for mood {mood.value}: {e}")
            return None

    async def _get_recently_played_tracks(
        self, server_id: int, hours: int = 2
    ) -> Set[str]:
        """Get tracks played recently in this server"""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT DISTINCT track_id FROM track_history
                    WHERE played_at > ?
                """,
                    (cutoff.isoformat(),),
                )

                return {row[0] for row in cursor.fetchall()}

        except Exception as e:
            self.logger.error(f"Error getting recently played tracks: {e}")
            return set()

    async def start_soundtrack_session(
        self,
        server_id: int,
        channel_id: int,
        started_by: int,
        initial_mood: MoodType = MoodType.CALM,
        auto_mode: bool = True,
    ) -> SoundtrackSession:
        """Start a new soundtrack session"""
        try:
            session = SoundtrackSession(
                id=str(uuid.uuid4()),
                server_id=server_id,
                channel_id=channel_id,
                started_by=started_by,
                current_mood=initial_mood,
                auto_mode=auto_mode,
            )

            self.active_sessions[channel_id] = session
            await self._save_session(session)

            self.logger.info(
                f"Started soundtrack session in channel {channel_id} with mood {initial_mood.value}"
            )
            return session

        except Exception as e:
            self.logger.error(f"Error starting soundtrack session: {e}")
            raise

    async def update_session_mood(
        self,
        channel_id: int,
        new_mood: MoodType,
        mood_snapshot: Optional[MoodSnapshot] = None,
    ) -> bool:
        """Update the mood of an active session"""
        try:
            if channel_id not in self.active_sessions:
                return False

            session = self.active_sessions[channel_id]
            session.current_mood = new_mood

            if mood_snapshot:
                session.mood_history.append(mood_snapshot)
                # Keep only last 20 snapshots
                session.mood_history = session.mood_history[-20:]

            await self._save_session(session)
            return True

        except Exception as e:
            self.logger.error(f"Error updating session mood: {e}")
            return False

    async def play_next_track(self, channel_id: int) -> Optional[MusicTrack]:
        """Select and set the next track for a session"""
        try:
            if channel_id not in self.active_sessions:
                return None

            session = self.active_sessions[channel_id]

            # Select track for current mood
            track = await self.select_track_for_mood(
                session.current_mood, session.server_id
            )

            if track:
                session.current_track = track
                session.track_started_at = datetime.now(timezone.utc)
                session.is_playing = True

                # Record play history
                await self._record_track_play(
                    track.id, channel_id, session.current_mood
                )

                # Update track stats
                track.play_count += 1
                track.last_played = session.track_started_at
                await self._save_track(track)

                await self._save_session(session)

            return track

        except Exception as e:
            self.logger.error(f"Error playing next track: {e}")
            return None

    async def _record_track_play(self, track_id: str, channel_id: int, mood: MoodType):
        """Record a track play in history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO track_history (id, track_id, channel_id, mood)
                    VALUES (?, ?, ?, ?)
                """,
                    (str(uuid.uuid4()), track_id, channel_id, mood.value),
                )
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error recording track play: {e}")

    async def stop_session(self, channel_id: int) -> bool:
        """Stop a soundtrack session"""
        try:
            if channel_id in self.active_sessions:
                session = self.active_sessions[channel_id]
                session.is_playing = False

                # Remove from database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM active_sessions WHERE channel_id = ?",
                        (channel_id,),
                    )
                    conn.commit()

                del self.active_sessions[channel_id]
                self.logger.info(f"Stopped soundtrack session in channel {channel_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error stopping session: {e}")
            return False

    async def add_track(
        self,
        title: str,
        artist: str,
        source: TrackSource,
        source_url: str,
        duration: int,
        added_by: int,
        mood_associations: Optional[Dict[MoodType, float]] = None,
        genre: MusicGenre = MusicGenre.AMBIENT,
    ) -> Optional[MusicTrack]:
        """Add a new music track to the library"""
        try:
            track_id = str(uuid.uuid4())

            track = MusicTrack(
                id=track_id,
                title=title,
                artist=artist,
                source=source,
                source_url=source_url,
                duration=duration,
                mood_associations=mood_associations or {},
                genre=genre,
                added_by=added_by,
            )

            await self._save_track(track)
            self.logger.info(f"Added track '{title}' by {artist} (ID: {track_id})")
            return track

        except Exception as e:
            self.logger.error(f"Error adding track: {e}")
            return None

    async def get_all_tracks(self) -> List[MusicTrack]:
        """Get all music tracks"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data FROM music_tracks")
                rows = cursor.fetchall()

                tracks = []
                for row in rows:
                    data = json.loads(row[0])
                    tracks.append(MusicTrack.from_dict(data))

                return tracks

        except Exception as e:
            self.logger.error(f"Error getting all tracks: {e}")
            return []

    async def get_tracks_for_mood(
        self, mood: MoodType, limit: int = 20
    ) -> List[MusicTrack]:
        """Get tracks suitable for a specific mood"""
        try:
            tracks = await self.get_all_tracks()

            # Sort by mood score
            mood_tracks = []
            for track in tracks:
                score = track.get_mood_score(mood)
                if score > 0:
                    mood_tracks.append((track, score))

            mood_tracks.sort(key=lambda x: x[1], reverse=True)
            return [track for track, _ in mood_tracks[:limit]]

        except Exception as e:
            self.logger.error(f"Error getting tracks for mood {mood.value}: {e}")
            return []

    async def get_session_stats(self, server_id: int) -> Dict[str, Any]:
        """Get soundtrack statistics for a server"""
        try:
            tracks = await self.get_all_tracks()

            # Get play history
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total plays
                cursor.execute("SELECT COUNT(*) FROM track_history")
                total_plays = cursor.fetchone()[0]

                # Plays by mood
                cursor.execute(
                    """
                    SELECT mood, COUNT(*) as count
                    FROM track_history
                    GROUP BY mood
                    ORDER BY count DESC
                """
                )
                mood_plays = cursor.fetchall()

                # Recent sessions
                cursor.execute(
                    """
                    SELECT COUNT(DISTINCT channel_id)
                    FROM active_sessions
                """
                )
                active_sessions = cursor.fetchone()[0]

            mood_play_dict = {row[0]: row[1] for row in mood_plays}

            return {
                "total_tracks": len(tracks),
                "total_plays": total_plays,
                "active_sessions": active_sessions,
                "mood_play_counts": mood_play_dict,
                "most_played_mood": (
                    max(mood_play_dict.items(), key=lambda x: x[1])
                    if mood_play_dict
                    else None
                ),
                "average_tracks_per_mood": len(tracks) / len(MoodType) if tracks else 0,
            }

        except Exception as e:
            self.logger.error(f"Error getting session stats: {e}")
            return {}

    async def _save_track(self, track: MusicTrack):
        """Save a track to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                data = json.dumps(track.to_dict())

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO music_tracks (id, data, added_at)
                    VALUES (?, ?, ?)
                """,
                    (track.id, data, track.added_at.isoformat()),
                )

                conn.commit()

        except Exception as e:
            self.logger.error(f"Error saving track {track.id}: {e}")
            raise

    async def _save_session(self, session: SoundtrackSession):
        """Save a session to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                data = json.dumps(session.to_dict())

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO active_sessions (channel_id, data, last_updated)
                    VALUES (?, ?, ?)
                """,
                    (session.channel_id, data, datetime.now(timezone.utc).isoformat()),
                )

                conn.commit()

        except Exception as e:
            self.logger.error(
                f"Error saving session for channel {session.channel_id}: {e}"
            )
            raise

    async def cleanup_expired_sessions(self):
        """Clean up sessions that haven't been updated recently"""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=24)  # 24 hours

            expired_channels = []
            for channel_id, session in self.active_sessions.items():
                if session.started_at < cutoff:
                    expired_channels.append(channel_id)

            for channel_id in expired_channels:
                await self.stop_session(channel_id)

            if expired_channels:
                self.logger.info(
                    f"Cleaned up {len(expired_channels)} expired soundtrack sessions"
                )

        except Exception as e:
            self.logger.error(f"Error cleaning up expired sessions: {e}")


# Global instance
_emotional_soundtrack_instance = None


def get_emotional_soundtrack() -> EmotionalSoundtrackSystem:
    """Get the global emotional soundtrack instance"""
    global _emotional_soundtrack_instance
    if _emotional_soundtrack_instance is None:
        _emotional_soundtrack_instance = EmotionalSoundtrackSystem()
    return _emotional_soundtrack_instance
