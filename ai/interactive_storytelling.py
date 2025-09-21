"""
Interactive Storytelling System
Enables collaborative story creation where community members can contribute to evolving narratives
"""

import asyncio
import json
import logging
import random
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import sqlite3
import hashlib

logger = logging.getLogger("astra.interactive_storytelling")


class StoryGenre(Enum):
    """Available story genres"""

    FANTASY = "fantasy"
    SCIFI = "sci-fi"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    HORROR = "horror"
    ADVENTURE = "adventure"
    COMEDY = "comedy"
    DRAMA = "drama"
    MIXED = "mixed"


class StoryStatus(Enum):
    """Story development status"""

    PLANNING = "planning"
    WRITING = "writing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ContributionType(Enum):
    """Types of story contributions"""

    PLOT_POINT = "plot_point"
    CHARACTER_DEVELOPMENT = "character_development"
    SETTING_DESCRIPTION = "setting_description"
    DIALOGUE = "dialogue"
    ACTION_SEQUENCE = "action_sequence"
    TWIST = "twist"
    ENDING = "ending"
    EDIT = "edit"


@dataclass
class StoryCharacter:
    """Represents a character in the story"""

    id: str
    name: str
    description: str
    traits: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(
        default_factory=dict
    )  # character_id -> relationship
    created_by: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "traits": self.traits,
            "relationships": self.relationships,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoryCharacter":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            traits=data.get("traits", []),
            relationships=data.get("relationships", {}),
            created_by=data.get("created_by", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


@dataclass
class StoryContribution:
    """Represents a contribution to a story"""

    id: str
    story_id: str
    contributor_id: int
    contribution_type: ContributionType
    content: str
    word_count: int = 0
    votes_up: int = 0
    votes_down: int = 0
    accepted: bool = False
    position: int = 0  # Order in the story
    parent_contribution_id: Optional[str] = None  # For branching stories
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "story_id": self.story_id,
            "contributor_id": self.contributor_id,
            "contribution_type": (
                self.contribution_type.value
                if hasattr(self.contribution_type, "value")
                else self.contribution_type
            ),
            "content": self.content,
            "word_count": self.word_count,
            "votes_up": self.votes_up,
            "votes_down": self.votes_down,
            "accepted": self.accepted,
            "position": self.position,
            "parent_contribution_id": self.parent_contribution_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoryContribution":
        return cls(
            id=data["id"],
            story_id=data["story_id"],
            contributor_id=data["contributor_id"],
            contribution_type=ContributionType(data["contribution_type"]),
            content=data["content"],
            word_count=data.get("word_count", 0),
            votes_up=data.get("votes_up", 0),
            votes_down=data.get("votes_down", 0),
            accepted=data.get("accepted", False),
            position=data.get("position", 0),
            parent_contribution_id=data.get("parent_contribution_id"),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


@dataclass
class InteractiveStory:
    """Represents an interactive, collaborative story"""

    id: str
    title: str
    description: str
    genre: StoryGenre
    status: StoryStatus
    server_id: int
    creator_id: int

    # Story content
    characters: Dict[str, StoryCharacter] = field(default_factory=dict)
    contributions: List[StoryContribution] = field(default_factory=list)
    current_summary: str = ""
    word_count: int = 0

    # Settings
    max_contributors: int = 10
    min_words_per_contribution: int = 50
    max_words_per_contribution: int = 500
    voting_enabled: bool = True
    anonymous_contributions: bool = False

    # Metadata
    tags: List[str] = field(default_factory=list)
    contributors: Set[int] = field(default_factory=set)
    view_count: int = 0
    favorite_count: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "genre": self.genre.value if hasattr(self.genre, "value") else self.genre,
            "status": (
                self.status.value if hasattr(self.status, "value") else self.status
            ),
            "server_id": self.server_id,
            "creator_id": self.creator_id,
            "characters": {
                cid: char.to_dict() for cid, char in self.characters.items()
            },
            "contributions": [contrib.to_dict() for contrib in self.contributions],
            "current_summary": self.current_summary,
            "word_count": self.word_count,
            "max_contributors": self.max_contributors,
            "min_words_per_contribution": self.min_words_per_contribution,
            "max_words_per_contribution": self.max_words_per_contribution,
            "voting_enabled": self.voting_enabled,
            "anonymous_contributions": self.anonymous_contributions,
            "tags": self.tags,
            "contributors": list(self.contributors),
            "view_count": self.view_count,
            "favorite_count": self.favorite_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InteractiveStory":
        story = cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            genre=StoryGenre(data["genre"]),
            status=StoryStatus(data["status"]),
            server_id=data["server_id"],
            creator_id=data["creator_id"],
            current_summary=data.get("current_summary", ""),
            word_count=data.get("word_count", 0),
            max_contributors=data.get("max_contributors", 10),
            min_words_per_contribution=data.get("min_words_per_contribution", 50),
            max_words_per_contribution=data.get("max_words_per_contribution", 500),
            voting_enabled=data.get("voting_enabled", True),
            anonymous_contributions=data.get("anonymous_contributions", False),
            tags=data.get("tags", []),
            contributors=set(data.get("contributors", [])),
            view_count=data.get("view_count", 0),
            favorite_count=data.get("favorite_count", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data.get("completed_at")
                else None
            ),
        )

        # Load characters
        for cid, char_data in data.get("characters", {}).items():
            story.characters[cid] = StoryCharacter.from_dict(char_data)

        # Load contributions
        for contrib_data in data.get("contributions", []):
            story.contributions.append(StoryContribution.from_dict(contrib_data))

        return story

    def get_accepted_contributions(self) -> List[StoryContribution]:
        """Get all accepted contributions in order"""
        accepted = [c for c in self.contributions if c.accepted]
        return sorted(accepted, key=lambda x: x.position)

    def get_pending_contributions(self) -> List[StoryContribution]:
        """Get all pending contributions"""
        return [c for c in self.contributions if not c.accepted]

    def get_full_story_text(self) -> str:
        """Get the complete story text from accepted contributions"""
        contributions = self.get_accepted_contributions()
        if not contributions:
            return self.description

        story_parts = []
        for contrib in contributions:
            story_parts.append(contrib.content)

        return "\n\n".join(story_parts)

    def add_contribution(self, contribution: StoryContribution) -> bool:
        """Add a contribution to the story"""
        # Check limits
        if (
            len(self.contributors) >= self.max_contributors
            and contribution.contributor_id not in self.contributors
        ):
            return False

        if not (
            self.min_words_per_contribution
            <= contribution.word_count
            <= self.max_words_per_contribution
        ):
            return False

        # Add contribution
        self.contributions.append(contribution)
        self.contributors.add(contribution.contributor_id)
        self.word_count += contribution.word_count
        self.updated_at = datetime.now(timezone.utc)

        return True

    def accept_contribution(self, contribution_id: str) -> bool:
        """Accept a contribution into the story"""
        for contrib in self.contributions:
            if contrib.id == contribution_id and not contrib.accepted:
                contrib.accepted = True
                # Set position if not set
                if contrib.position == 0:
                    max_pos = max((c.position for c in self.contributions), default=0)
                    contrib.position = max_pos + 1
                self.updated_at = datetime.now(timezone.utc)
                return True
        return False

    def generate_summary(self) -> str:
        """Generate a summary of the current story state"""
        if not self.contributions:
            return f"A {self.genre.value} story called '{self.title}' is being planned."

        accepted_count = len(self.get_accepted_contributions())
        pending_count = len(self.get_pending_contributions())

        summary = f"'{self.title}' is a {self.genre.value} story with {accepted_count} accepted contributions"
        if pending_count > 0:
            summary += f" and {pending_count} pending contributions"
        summary += f". {len(self.contributors)} community members have contributed {self.word_count} words."

        return summary


class InteractiveStorytellingEngine:
    """Main engine for interactive storytelling"""

    def __init__(self):
        self.logger = logger
        self.stories: Dict[str, InteractiveStory] = {}

        # Database setup
        self.db_path = Path("data/interactive_storytelling.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._setup_database()

        logger.info("Interactive Storytelling Engine initialized")

    def _setup_database(self):
        """Setup database for story storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Stories table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS stories (
                        id TEXT PRIMARY KEY,
                        server_id INTEGER NOT NULL,
                        story_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Story votes table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS story_votes (
                        story_id TEXT,
                        contribution_id TEXT,
                        user_id INTEGER,
                        vote_type TEXT, -- 'up' or 'down'
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (story_id, contribution_id, user_id)
                    )
                """
                )

                # Story favorites table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS story_favorites (
                        story_id TEXT,
                        user_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (story_id, user_id)
                    )
                """
                )

                # Create indexes
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_stories_server_id ON stories (server_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_stories_created_at ON stories (created_at)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_story_votes_story ON story_votes (story_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_story_favorites_story ON story_favorites (story_id)"
                )

                conn.commit()
                logger.info("Interactive storytelling database initialized")

        except Exception as e:
            logger.error(f"Database setup error: {e}")

    async def create_story(
        self,
        server_id: int,
        creator_id: int,
        title: str,
        description: str,
        genre: StoryGenre,
        **settings,
    ) -> InteractiveStory:
        """Create a new interactive story"""
        story_id = f"story_{server_id}_{int(datetime.now(timezone.utc).timestamp())}_{random.randint(1000, 9999)}"

        story = InteractiveStory(
            id=story_id,
            title=title,
            description=description,
            genre=genre,
            status=StoryStatus.PLANNING,
            server_id=server_id,
            creator_id=creator_id,
            **settings,
        )

        self.stories[story_id] = story
        await self._save_story(story)

        logger.info(f"Created new story: {title} ({story_id})")
        return story

    async def get_story(self, story_id: str) -> Optional[InteractiveStory]:
        """Get a story by ID"""
        if story_id in self.stories:
            return self.stories[story_id]

        # Load from database
        story = await self._load_story(story_id)
        if story:
            self.stories[story_id] = story
        return story

    async def get_server_stories(
        self, server_id: int, status: Optional[StoryStatus] = None
    ) -> List[InteractiveStory]:
        """Get all stories for a server"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if status:
                    cursor.execute(
                        "SELECT story_data FROM stories WHERE server_id = ? AND json_extract(story_data, '$.status') = ? ORDER BY json_extract(story_data, '$.updated_at') DESC",
                        (server_id, status.value),
                    )
                else:
                    cursor.execute(
                        "SELECT story_data FROM stories WHERE server_id = ? ORDER BY json_extract(story_data, '$.updated_at') DESC",
                        (server_id,),
                    )

                stories = []
                for row in cursor.fetchall():
                    story_data = json.loads(row[0])
                    story = InteractiveStory.from_dict(story_data)
                    self.stories[story.id] = story
                    stories.append(story)

                return stories

        except Exception as e:
            logger.error(f"Error loading server stories: {e}")
            return []

    async def add_contribution(
        self,
        story_id: str,
        contributor_id: int,
        contribution_type: ContributionType,
        content: str,
        **metadata,
    ) -> Optional[StoryContribution]:
        """Add a contribution to a story"""
        story = await self.get_story(story_id)
        if not story or story.status not in [StoryStatus.WRITING, StoryStatus.PLANNING]:
            return None

        # Create contribution
        contrib_id = f"contrib_{story_id}_{int(datetime.now(timezone.utc).timestamp())}_{random.randint(1000, 9999)}"
        word_count = len(content.split())

        contribution = StoryContribution(
            id=contrib_id,
            story_id=story_id,
            contributor_id=contributor_id,
            contribution_type=contribution_type,
            content=content,
            word_count=word_count,
            metadata=metadata,
        )

        # Add to story
        if story.add_contribution(contribution):
            await self._save_story(story)
            logger.info(f"Added contribution to story {story_id}: {word_count} words")
            return contribution

        return None

    async def vote_on_contribution(
        self, story_id: str, contribution_id: str, user_id: int, vote_up: bool
    ) -> bool:
        """Vote on a contribution"""
        story = await self.get_story(story_id)
        if not story or not story.voting_enabled:
            return False

        # Find contribution
        contribution = None
        for contrib in story.contributions:
            if contrib.id == contribution_id:
                contribution = contrib
                break

        if not contribution:
            return False

        # Record vote in database
        try:
            with sqlite3.connect(self.db_path) as conn:
                vote_type = "up" if vote_up else "down"
                conn.execute(
                    """
                    INSERT OR REPLACE INTO story_votes
                    (story_id, contribution_id, user_id, vote_type)
                    VALUES (?, ?, ?, ?)
                """,
                    (story_id, contribution_id, user_id, vote_type),
                )
                conn.commit()

                # Update contribution vote counts
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM story_votes WHERE contribution_id = ? AND vote_type = 'up'",
                    (contribution_id,),
                )
                contribution.votes_up = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM story_votes WHERE contribution_id = ? AND vote_type = 'down'",
                    (contribution_id,),
                )
                contribution.votes_down = cursor.fetchone()[0]

                await self._save_story(story)
                return True

        except Exception as e:
            logger.error(f"Error recording vote: {e}")
            return False

    async def accept_contribution(self, story_id: str, contribution_id: str) -> bool:
        """Accept a contribution into the story"""
        story = await self.get_story(story_id)
        if not story:
            return False

        if story.accept_contribution(contribution_id):
            await self._save_story(story)
            logger.info(f"Accepted contribution {contribution_id} in story {story_id}")
            return True

        return False

    async def add_character(
        self,
        story_id: str,
        creator_id: int,
        name: str,
        description: str,
        traits: List[str] = None,
    ) -> Optional[StoryCharacter]:
        """Add a character to a story"""
        story = await self.get_story(story_id)
        if not story:
            return None

        char_id = f"char_{story_id}_{int(datetime.now(timezone.utc).timestamp())}_{random.randint(1000, 9999)}"

        character = StoryCharacter(
            id=char_id,
            name=name,
            description=description,
            traits=traits or [],
            created_by=creator_id,
        )

        story.characters[char_id] = character
        await self._save_story(story)

        logger.info(f"Added character {name} to story {story_id}")
        return character

    async def toggle_favorite(self, story_id: str, user_id: int) -> bool:
        """Toggle favorite status for a story"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if already favorited
                cursor.execute(
                    "SELECT 1 FROM story_favorites WHERE story_id = ? AND user_id = ?",
                    (story_id, user_id),
                )

                if cursor.fetchone():
                    # Remove favorite
                    conn.execute(
                        "DELETE FROM story_favorites WHERE story_id = ? AND user_id = ?",
                        (story_id, user_id),
                    )
                    # Update story favorite count
                    story = await self.get_story(story_id)
                    if story:
                        story.favorite_count = max(0, story.favorite_count - 1)
                        await self._save_story(story)
                    return False  # Removed favorite
                else:
                    # Add favorite
                    conn.execute(
                        "INSERT INTO story_favorites (story_id, user_id) VALUES (?, ?)",
                        (story_id, user_id),
                    )
                    # Update story favorite count
                    story = await self.get_story(story_id)
                    if story:
                        story.favorite_count += 1
                        await self._save_story(story)
                    return True  # Added favorite

                conn.commit()

        except Exception as e:
            logger.error(f"Error toggling favorite: {e}")
            return False

    async def _save_story(self, story: InteractiveStory):
        """Save story to database"""
        try:
            story_data = story.to_dict()

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO stories
                    (id, server_id, story_data, updated_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        story.id,
                        story.server_id,
                        json.dumps(story_data),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"Error saving story {story.id}: {e}")

    async def _load_story(self, story_id: str) -> Optional[InteractiveStory]:
        """Load story from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT story_data FROM stories WHERE id = ?", (story_id,)
                )

                row = cursor.fetchone()
                if row:
                    story_data = json.loads(row[0])
                    return InteractiveStory.from_dict(story_data)

        except Exception as e:
            logger.error(f"Error loading story {story_id}: {e}")

        return None

    async def get_story_stats(self, server_id: int) -> Dict[str, Any]:
        """Get storytelling statistics for a server"""
        stories = await self.get_server_stories(server_id)

        stats = {
            "total_stories": len(stories),
            "active_stories": len(
                [
                    s
                    for s in stories
                    if s.status in [StoryStatus.WRITING, StoryStatus.REVIEWING]
                ]
            ),
            "completed_stories": len(
                [s for s in stories if s.status == StoryStatus.COMPLETED]
            ),
            "total_contributions": sum(len(s.contributions) for s in stories),
            "total_words": sum(s.word_count for s in stories),
            "unique_contributors": len(
                set(c.creator_id for s in stories for c in s.contributions)
            ),
            "most_popular_genre": None,
            "average_story_length": 0,
        }

        if stories:
            # Find most popular genre
            genre_counts = {}
            for story in stories:
                genre_counts[story.genre] = genre_counts.get(story.genre, 0) + 1
            stats["most_popular_genre"] = (
                max(genre_counts.items(), key=lambda x: x[1])[0].value
                if genre_counts
                else None
            )

            # Average story length
            completed_stories = [
                s
                for s in stories
                if s.status == StoryStatus.COMPLETED and s.word_count > 0
            ]
            if completed_stories:
                stats["average_story_length"] = sum(
                    s.word_count for s in completed_stories
                ) / len(completed_stories)

        return stats


# Global storytelling engine instance
_storytelling_engine: Optional[InteractiveStorytellingEngine] = None


def get_storytelling_engine() -> InteractiveStorytellingEngine:
    """Get the global storytelling engine instance"""
    global _storytelling_engine
    if _storytelling_engine is None:
        _storytelling_engine = InteractiveStorytellingEngine()
    return _storytelling_engine


def initialize_storytelling_engine() -> InteractiveStorytellingEngine:
    """Initialize the global storytelling engine"""
    global _storytelling_engine
    _storytelling_engine = InteractiveStorytellingEngine()
    return _storytelling_engine
