"""
Collaborative Creativity Hub
A system for collaborative creative projects and brainstorming
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid


class ProjectType(Enum):
    """Types of creative projects"""

    ART = "art"
    MUSIC = "music"
    WRITING = "writing"
    CODING = "coding"
    DESIGN = "design"
    FILM = "film"
    GAME = "game"
    OTHER = "other"


class ProjectStatus(Enum):
    """Project status states"""

    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectRole(Enum):
    """Roles in a creative project"""

    LEADER = "leader"
    CONTRIBUTOR = "contributor"
    REVIEWER = "reviewer"
    MENTOR = "mentor"
    COLLABORATOR = "collaborator"


class IdeaStatus(Enum):
    """Status of brainstormed ideas"""

    PROPOSED = "proposed"
    DISCUSSING = "discussing"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


@dataclass
class ProjectMember:
    """A member of a creative project"""

    user_id: int
    role: ProjectRole
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    contributions: int = 0
    skills: List[str] = field(default_factory=list)
    availability: str = "flexible"  # flexible, busy, available

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role": self.role.value if hasattr(self.role, "value") else self.role,
            "joined_at": self.joined_at.isoformat(),
            "contributions": self.contributions,
            "skills": self.skills,
            "availability": self.availability,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectMember":
        return cls(
            user_id=data["user_id"],
            role=ProjectRole(data["role"]),
            joined_at=datetime.fromisoformat(data["joined_at"]),
            contributions=data.get("contributions", 0),
            skills=data.get("skills", []),
            availability=data.get("availability", "flexible"),
        )


@dataclass
class ProjectMilestone:
    """A milestone in a creative project"""

    id: str
    title: str
    description: str
    due_date: Optional[datetime] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    assigned_to: Optional[int] = None
    progress: int = 0  # 0-100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed": self.completed,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "assigned_to": self.assigned_to,
            "progress": self.progress,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectMilestone":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            due_date=(
                datetime.fromisoformat(data["due_date"])
                if data.get("due_date")
                else None
            ),
            completed=data.get("completed", False),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data.get("completed_at")
                else None
            ),
            assigned_to=data.get("assigned_to"),
            progress=data.get("progress", 0),
        )


@dataclass
class BrainstormIdea:
    """An idea from brainstorming session"""

    id: str
    content: str
    author_id: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: IdeaStatus = IdeaStatus.PROPOSED
    votes: int = 0
    tags: List[str] = field(default_factory=list)
    discussion_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "author_id": self.author_id,
            "created_at": self.created_at.isoformat(),
            "status": (
                self.status.value if hasattr(self.status, "value") else self.status
            ),
            "votes": self.votes,
            "tags": self.tags,
            "discussion_count": self.discussion_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrainstormIdea":
        return cls(
            id=data["id"],
            content=data["content"],
            author_id=data["author_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            status=IdeaStatus(data.get("status", "proposed")),
            votes=data.get("votes", 0),
            tags=data.get("tags", []),
            discussion_count=data.get("discussion_count", 0),
        )


@dataclass
class CreativeProject:
    """A collaborative creative project"""

    id: str
    server_id: int
    creator_id: int
    title: str
    description: str
    project_type: ProjectType
    status: ProjectStatus = ProjectStatus.PLANNING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deadline: Optional[datetime] = None
    max_members: int = 10
    required_skills: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    visibility: str = "public"  # public, private, invite_only

    # Dynamic data
    members: Dict[int, ProjectMember] = field(default_factory=dict)
    milestones: Dict[str, ProjectMilestone] = field(default_factory=dict)
    ideas: Dict[str, BrainstormIdea] = field(default_factory=dict)
    resources: List[Dict[str, Any]] = field(default_factory=list)

    # Statistics
    view_count: int = 0
    favorite_count: int = 0
    total_contributions: int = 0
    completion_percentage: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "server_id": self.server_id,
            "creator_id": self.creator_id,
            "title": self.title,
            "description": self.description,
            "project_type": (
                self.project_type.value
                if hasattr(self.project_type, "value")
                else self.project_type
            ),
            "status": (
                self.status.value if hasattr(self.status, "value") else self.status
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "max_members": self.max_members,
            "required_skills": self.required_skills,
            "tags": self.tags,
            "visibility": self.visibility,
            "members": {str(k): v.to_dict() for k, v in self.members.items()},
            "milestones": {k: v.to_dict() for k, v in self.milestones.items()},
            "ideas": {k: v.to_dict() for k, v in self.ideas.items()},
            "resources": self.resources,
            "view_count": self.view_count,
            "favorite_count": self.favorite_count,
            "total_contributions": self.total_contributions,
            "completion_percentage": self.completion_percentage,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreativeProject":
        project = cls(
            id=data["id"],
            server_id=data["server_id"],
            creator_id=data["creator_id"],
            title=data["title"],
            description=data["description"],
            project_type=ProjectType(data["project_type"]),
            status=ProjectStatus(data.get("status", "planning")),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            deadline=(
                datetime.fromisoformat(data["deadline"])
                if data.get("deadline")
                else None
            ),
            max_members=data.get("max_members", 10),
            required_skills=data.get("required_skills", []),
            tags=data.get("tags", []),
            visibility=data.get("visibility", "public"),
            view_count=data.get("view_count", 0),
            favorite_count=data.get("favorite_count", 0),
            total_contributions=data.get("total_contributions", 0),
            completion_percentage=data.get("completion_percentage", 0),
        )

        # Load members
        for user_id_str, member_data in data.get("members", {}).items():
            project.members[int(user_id_str)] = ProjectMember.from_dict(member_data)

        # Load milestones
        for milestone_id, milestone_data in data.get("milestones", {}).items():
            project.milestones[milestone_id] = ProjectMilestone.from_dict(
                milestone_data
            )

        # Load ideas
        for idea_id, idea_data in data.get("ideas", {}).items():
            project.ideas[idea_id] = BrainstormIdea.from_dict(idea_data)

        # Load resources
        project.resources = data.get("resources", [])

        return project

    def get_active_members(self) -> List[ProjectMember]:
        """Get list of active project members"""
        return [
            member
            for member in self.members.values()
            if member.availability != "inactive"
        ]

    def get_completion_percentage(self) -> int:
        """Calculate project completion percentage"""
        if not self.milestones:
            return 0

        completed_milestones = sum(1 for m in self.milestones.values() if m.completed)
        total_milestones = len(self.milestones)

        if total_milestones == 0:
            return 0

        return int((completed_milestones / total_milestones) * 100)

    def update_completion_percentage(self):
        """Update the completion percentage"""
        self.completion_percentage = self.get_completion_percentage()


class CollaborativeCreativityHub:
    """Main hub for collaborative creative projects"""

    def __init__(self, db_path: str = "data/creativity_hub.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("astra.creativity_hub")
        self._init_database()

    def _init_database(self):
        """Initialize the database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Projects table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    server_id INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Project favorites
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS project_favorites (
                    project_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    favorited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (project_id, user_id)
                )
            """
            )

            # Idea votes
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS idea_votes (
                    idea_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    vote_type TEXT NOT NULL, -- up, down
                    voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (idea_id, user_id)
                )
            """
            )

            # Project discussions/comments
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS project_discussions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    discussion_type TEXT NOT NULL, -- general, milestone, idea
                    reference_id TEXT, -- milestone_id or idea_id
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()

    async def create_project(
        self,
        server_id: int,
        creator_id: int,
        title: str,
        description: str,
        project_type: ProjectType,
        deadline: Optional[datetime] = None,
        max_members: int = 10,
        required_skills: List[str] = None,
        tags: List[str] = None,
        visibility: str = "public",
    ) -> Optional[CreativeProject]:
        """Create a new creative project"""
        try:
            project_id = str(uuid.uuid4())

            project = CreativeProject(
                id=project_id,
                server_id=server_id,
                creator_id=creator_id,
                title=title,
                description=description,
                project_type=project_type,
                deadline=deadline,
                max_members=max_members,
                required_skills=required_skills or [],
                tags=tags or [],
                visibility=visibility,
            )

            # Add creator as leader
            creator_member = ProjectMember(
                user_id=creator_id,
                role=ProjectRole.LEADER,
                skills=[],  # Will be filled by user
            )
            project.members[creator_id] = creator_member

            # Save to database
            await self._save_project(project)

            self.logger.info(
                f"Created project '{title}' (ID: {project_id}) in server {server_id}"
            )
            return project

        except Exception as e:
            self.logger.error(f"Error creating project: {e}")
            return None

    async def get_project(self, project_id: str) -> Optional[CreativeProject]:
        """Get a project by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data FROM projects WHERE id = ?", (project_id,))
                row = cursor.fetchone()

                if row:
                    data = json.loads(row[0])
                    return CreativeProject.from_dict(data)

        except Exception as e:
            self.logger.error(f"Error getting project {project_id}: {e}")

        return None

    async def get_server_projects(
        self,
        server_id: int,
        status_filter: Optional[ProjectStatus] = None,
        type_filter: Optional[ProjectType] = None,
        limit: int = 50,
    ) -> List[CreativeProject]:
        """Get all projects for a server with optional filters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = "SELECT data FROM projects WHERE server_id = ?"
                params = [server_id]

                if status_filter:
                    # This would require loading and filtering in Python
                    # For simplicity, we'll load all and filter
                    pass

                cursor.execute(query, params)
                rows = cursor.fetchall()

                projects = []
                for row in rows:
                    data = json.loads(row[0])
                    project = CreativeProject.from_dict(data)

                    # Apply filters
                    if status_filter and project.status != status_filter:
                        continue
                    if type_filter and project.project_type != type_filter:
                        continue

                    projects.append(project)

                # Sort by creation date (newest first)
                projects.sort(key=lambda p: p.created_at, reverse=True)

                return projects[:limit]

        except Exception as e:
            self.logger.error(f"Error getting server projects: {e}")
            return []

    async def update_project(self, project: CreativeProject) -> bool:
        """Update a project"""
        try:
            project.updated_at = datetime.now(timezone.utc)
            project.update_completion_percentage()

            await self._save_project(project)
            return True

        except Exception as e:
            self.logger.error(f"Error updating project {project.id}: {e}")
            return False

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Delete related data first
                cursor.execute(
                    "DELETE FROM project_favorites WHERE project_id = ?", (project_id,)
                )
                cursor.execute(
                    "DELETE FROM idea_votes WHERE project_id = ?", (project_id,)
                )
                cursor.execute(
                    "DELETE FROM project_discussions WHERE project_id = ?",
                    (project_id,),
                )

                # Delete project
                cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
                conn.commit()

                return cursor.rowcount > 0

        except Exception as e:
            self.logger.error(f"Error deleting project {project_id}: {e}")
            return False

    async def join_project(
        self, project_id: str, user_id: int, skills: List[str] = None
    ) -> bool:
        """Join a creative project"""
        try:
            project = await self.get_project(project_id)
            if not project:
                return False

            if len(project.members) >= project.max_members:
                return False

            if user_id in project.members:
                return False  # Already a member

            member = ProjectMember(
                user_id=user_id,
                role=ProjectRole.CONTRIBUTOR,
                skills=skills or [],
            )

            project.members[user_id] = member
            await self.update_project(project)
            return True

        except Exception as e:
            self.logger.error(f"Error joining project {project_id}: {e}")
            return False

    async def leave_project(self, project_id: str, user_id: int) -> bool:
        """Leave a creative project"""
        try:
            project = await self.get_project(project_id)
            if not project or user_id not in project.members:
                return False

            # Can't leave if you're the only leader
            member = project.members[user_id]
            if member.role == ProjectRole.LEADER:
                leaders = sum(
                    1 for m in project.members.values() if m.role == ProjectRole.LEADER
                )
                if leaders <= 1:
                    return False  # Need at least one leader

            del project.members[user_id]
            await self.update_project(project)
            return True

        except Exception as e:
            self.logger.error(f"Error leaving project {project_id}: {e}")
            return False

    async def add_milestone(
        self,
        project_id: str,
        title: str,
        description: str,
        due_date: Optional[datetime] = None,
        assigned_to: Optional[int] = None,
    ) -> Optional[ProjectMilestone]:
        """Add a milestone to a project"""
        try:
            project = await self.get_project(project_id)
            if not project:
                return None

            milestone_id = str(uuid.uuid4())
            milestone = ProjectMilestone(
                id=milestone_id,
                title=title,
                description=description,
                due_date=due_date,
                assigned_to=assigned_to,
            )

            project.milestones[milestone_id] = milestone
            await self.update_project(project)
            return milestone

        except Exception as e:
            self.logger.error(f"Error adding milestone to project {project_id}: {e}")
            return None

    async def add_brainstorm_idea(
        self,
        project_id: str,
        author_id: int,
        content: str,
        tags: List[str] = None,
    ) -> Optional[BrainstormIdea]:
        """Add a brainstorm idea to a project"""
        try:
            project = await self.get_project(project_id)
            if not project:
                return None

            idea_id = str(uuid.uuid4())
            idea = BrainstormIdea(
                id=idea_id,
                content=content,
                author_id=author_id,
                tags=tags or [],
            )

            project.ideas[idea_id] = idea
            await self.update_project(project)
            return idea

        except Exception as e:
            self.logger.error(
                f"Error adding brainstorm idea to project {project_id}: {e}"
            )
            return None

    async def vote_on_idea(
        self,
        project_id: str,
        idea_id: str,
        user_id: int,
        vote_up: bool = True,
    ) -> bool:
        """Vote on a brainstorm idea"""
        try:
            project = await self.get_project(project_id)
            if not project or idea_id not in project.ideas:
                return False

            idea = project.ideas[idea_id]

            # Check if user already voted
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT vote_type FROM idea_votes WHERE idea_id = ? AND user_id = ?",
                    (idea_id, user_id),
                )
                existing_vote = cursor.fetchone()

                if existing_vote:
                    old_vote = existing_vote[0]
                    if (vote_up and old_vote == "up") or (
                        not vote_up and old_vote == "down"
                    ):
                        # Same vote, remove it
                        cursor.execute(
                            "DELETE FROM idea_votes WHERE idea_id = ? AND user_id = ?",
                            (idea_id, user_id),
                        )
                        idea.votes += -1 if vote_up else 1
                    else:
                        # Different vote, update it
                        cursor.execute(
                            "UPDATE idea_votes SET vote_type = ? WHERE idea_id = ? AND user_id = ?",
                            ("up" if vote_up else "down", idea_id, user_id),
                        )
                        idea.votes += 1 if vote_up else -1
                else:
                    # New vote
                    cursor.execute(
                        "INSERT INTO idea_votes (idea_id, project_id, user_id, vote_type) VALUES (?, ?, ?, ?)",
                        (idea_id, project_id, user_id, "up" if vote_up else "down"),
                    )
                    idea.votes += 1 if vote_up else -1

                conn.commit()

            await self.update_project(project)
            return True

        except Exception as e:
            self.logger.error(f"Error voting on idea {idea_id}: {e}")
            return False

    async def toggle_favorite(self, project_id: str, user_id: int) -> bool:
        """Toggle favorite status for a project"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if already favorited
                cursor.execute(
                    "SELECT 1 FROM project_favorites WHERE project_id = ? AND user_id = ?",
                    (project_id, user_id),
                )

                if cursor.fetchone():
                    # Remove favorite
                    cursor.execute(
                        "DELETE FROM project_favorites WHERE project_id = ? AND user_id = ?",
                        (project_id, user_id),
                    )
                    # Update project favorite count
                    project = await self.get_project(project_id)
                    if project:
                        project.favorite_count -= 1
                        await self.update_project(project)
                    return False  # Removed
                else:
                    # Add favorite
                    cursor.execute(
                        "INSERT INTO project_favorites (project_id, user_id) VALUES (?, ?)",
                        (project_id, user_id),
                    )
                    # Update project favorite count
                    project = await self.get_project(project_id)
                    if project:
                        project.favorite_count += 1
                        await self.update_project(project)
                    return True  # Added

                conn.commit()

        except Exception as e:
            self.logger.error(f"Error toggling favorite for project {project_id}: {e}")
            return False

    async def get_project_stats(self, server_id: int) -> Dict[str, Any]:
        """Get creativity hub statistics for a server"""
        try:
            projects = await self.get_server_projects(server_id)

            stats = {
                "total_projects": len(projects),
                "active_projects": sum(
                    1 for p in projects if p.status == ProjectStatus.ACTIVE
                ),
                "completed_projects": sum(
                    1 for p in projects if p.status == ProjectStatus.COMPLETED
                ),
                "total_members": sum(len(p.members) for p in projects),
                "total_milestones": sum(len(p.milestones) for p in projects),
                "total_ideas": sum(len(p.ideas) for p in projects),
                "most_popular_type": None,
                "average_completion": 0,
            }

            # Calculate most popular type
            type_counts = {}
            total_completion = 0

            for project in projects:
                type_counts[project.project_type.value] = (
                    type_counts.get(project.project_type.value, 0) + 1
                )
                total_completion += project.completion_percentage

            if type_counts:
                stats["most_popular_type"] = max(type_counts, key=type_counts.get)

            if projects:
                stats["average_completion"] = total_completion // len(projects)

            return stats

        except Exception as e:
            self.logger.error(
                f"Error getting project stats for server {server_id}: {e}"
            )
            return {}

    async def _save_project(self, project: CreativeProject):
        """Save a project to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                data = json.dumps(project.to_dict())

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO projects (id, server_id, data, updated_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        project.id,
                        project.server_id,
                        data,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )

                conn.commit()

        except Exception as e:
            self.logger.error(f"Error saving project {project.id}: {e}")
            raise


# Global instance
_creativity_hub_instance = None


def get_creativity_hub() -> CollaborativeCreativityHub:
    """Get the global creativity hub instance"""
    global _creativity_hub_instance
    if _creativity_hub_instance is None:
        _creativity_hub_instance = CollaborativeCreativityHub()
    return _creativity_hub_instance
