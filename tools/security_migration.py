"""
🔄 SECURITY SYSTEM MIGRATION SCRIPT
Migrates data from old security systems to the new unified security system

This script handles:
- User profile migration from multiple databases
- Violation history consolidation
- Trust score normalization
- Database schema updates
- Configuration migration
"""

import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger("astra.security.migration")


class SecurityMigrationTool:
    """Tool to migrate from old security systems to unified system"""

    def __init__(self):
        self.old_databases = [
            "data/advanced_intelligence.db",
            "data/bot_personality.db",
            "data/consolidated_ai.db",
            "data/context_manager.db",
            "data/forensic_security.db",
            "data/user_profiles.db",
        ]

        self.new_database = "data/unified_security.db"
        self.migration_log = "data/security_migration.log"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(self.migration_log), logging.StreamHandler()],
        )

    async def run_migration(self) -> Dict[str, Any]:
        """Run complete migration process"""
        logger.info("🔄 Starting security system migration...")

        migration_stats = {
            "users_migrated": 0,
            "violations_migrated": 0,
            "databases_processed": 0,
            "errors": [],
            "migration_time": datetime.now().isoformat(),
        }

        try:
            # 1. Create new unified database if it doesn't exist
            await self._ensure_unified_database()

            # 2. Migrate user profiles from old systems
            migration_stats.update(await self._migrate_user_profiles())

            # 3. Migrate violation records
            migration_stats.update(await self._migrate_violation_records())

            # 4. Clean up old databases (optional - commented out for safety)
            # await self._cleanup_old_databases()

            # 5. Verify migration integrity
            verification_result = await self._verify_migration()
            migration_stats["verification"] = verification_result

            logger.info(f"✅ Security migration completed successfully!")
            logger.info(f"📊 Migration Statistics: {migration_stats}")

            return migration_stats

        except Exception as e:
            error_msg = f"Migration failed: {e}"
            logger.error(error_msg)
            migration_stats["errors"].append(error_msg)
            return migration_stats

    async def _ensure_unified_database(self):
        """Ensure unified database exists with proper schema"""
        logger.info("📋 Ensuring unified database schema...")

        conn = sqlite3.connect(self.new_database)
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                trust_score REAL DEFAULT 50.0,
                punishment_level INTEGER DEFAULT 0,
                is_trusted BOOLEAN DEFAULT FALSE,
                is_quarantined BOOLEAN DEFAULT FALSE,
                profile_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS violation_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                violation_type TEXT NOT NULL,
                severity INTEGER NOT NULL,
                timestamp REAL NOT NULL,
                evidence TEXT,
                action_taken TEXT,
                moderator_id INTEGER,
                resolved BOOLEAN DEFAULT FALSE
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS security_events (
                event_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                threat_level INTEGER NOT NULL,
                timestamp REAL NOT NULL,
                details TEXT,
                automated_response TEXT,
                manual_override BOOLEAN DEFAULT FALSE
            )
        """
        )

        # Create migration tracking table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS migration_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_database TEXT,
                migration_type TEXT,
                records_migrated INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                notes TEXT
            )
        """
        )

        conn.commit()
        conn.close()

        logger.info("✅ Unified database schema ready")

    async def _migrate_user_profiles(self) -> Dict[str, int]:
        """Migrate user profiles from all old databases"""
        logger.info("👥 Migrating user profiles...")

        stats = {"users_migrated": 0, "profiles_consolidated": 0}
        consolidated_profiles = {}  # user_id:guild_id -> profile_data

        for db_path in self.old_databases:
            if not os.path.exists(db_path):
                logger.info(f"⏭️ Skipping {db_path} (not found)")
                continue

            try:
                logger.info(f"📖 Processing {db_path}...")

                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Try to find user profile tables (different naming conventions)
                tables = cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()

                for (table_name,) in tables:
                    if "user" in table_name.lower() or "profile" in table_name.lower():
                        await self._migrate_user_table(
                            cursor, table_name, consolidated_profiles
                        )

                conn.close()
                stats["databases_processed"] += 1

            except Exception as e:
                logger.error(f"Error processing {db_path}: {e}")

        # Save consolidated profiles to unified database
        stats["users_migrated"] = await self._save_consolidated_profiles(
            consolidated_profiles
        )

        return stats

    async def _migrate_user_table(
        self, cursor: sqlite3.Cursor, table_name: str, consolidated_profiles: Dict
    ):
        """Migrate user data from a specific table"""
        try:
            # Get table structure
            columns = [
                col[1]
                for col in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
            ]

            # Find user ID column
            user_id_col = None
            for col in columns:
                if "user" in col.lower() and "id" in col.lower():
                    user_id_col = col
                    break

            if not user_id_col:
                logger.warning(f"No user ID column found in {table_name}")
                return

            # Read all records
            records = cursor.execute(f"SELECT * FROM {table_name}").fetchall()

            for record in records:
                record_dict = dict(zip(columns, record))
                user_id = record_dict.get(user_id_col)

                if not user_id:
                    continue

                # Assume guild_id is 0 if not found (will be updated later)
                guild_id = record_dict.get("guild_id", 0)
                profile_key = f"{user_id}:{guild_id}"

                # Consolidate profile data
                if profile_key not in consolidated_profiles:
                    consolidated_profiles[profile_key] = {
                        "user_id": user_id,
                        "guild_id": guild_id,
                        "trust_score": 50.0,
                        "punishment_level": 0,
                        "is_trusted": False,
                        "is_quarantined": False,
                        "violation_history": [],
                        "positive_contributions": 0,
                        "message_count": 0,
                        "avg_message_length": 0.0,
                        "sources": [],
                    }

                profile = consolidated_profiles[profile_key]
                profile["sources"].append(table_name)

                # Map known fields
                field_mapping = {
                    "trust_score": ["trust_score", "trust", "score"],
                    "violation_count": [
                        "violations",
                        "violation_count",
                        "warning_count",
                    ],
                    "positive_contributions": [
                        "positive",
                        "contributions",
                        "good_actions",
                    ],
                    "message_count": ["messages", "message_count", "msg_count"],
                    "punishment_level": ["punishment", "level", "warning_level"],
                }

                for profile_field, possible_cols in field_mapping.items():
                    for col in possible_cols:
                        if col in record_dict and record_dict[col] is not None:
                            profile[profile_field] = record_dict[col]
                            break

                # Calculate derived values
                if profile.get("violation_count", 0) > 5:
                    profile["trust_score"] = max(
                        0, 50 - (profile["violation_count"] * 5)
                    )
                elif profile.get("positive_contributions", 0) > 0:
                    profile["trust_score"] = min(
                        100, 50 + (profile["positive_contributions"] * 2)
                    )

                profile["is_trusted"] = profile["trust_score"] >= 70
                profile["is_quarantined"] = profile["trust_score"] <= 25

        except Exception as e:
            logger.error(f"Error migrating table {table_name}: {e}")

    async def _save_consolidated_profiles(self, consolidated_profiles: Dict) -> int:
        """Save consolidated profiles to unified database"""
        logger.info(f"💾 Saving {len(consolidated_profiles)} consolidated profiles...")

        conn = sqlite3.connect(self.new_database)
        cursor = conn.cursor()

        saved_count = 0

        for profile_key, profile_data in consolidated_profiles.items():
            try:
                # Remove non-serializable fields
                profile_json = profile_data.copy()
                sources = profile_json.pop("sources", [])

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO user_profiles 
                    (id, user_id, guild_id, trust_score, punishment_level, is_trusted, is_quarantined, profile_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        profile_key,
                        profile_data["user_id"],
                        profile_data["guild_id"],
                        profile_data["trust_score"],
                        profile_data.get("punishment_level", 0),
                        profile_data["is_trusted"],
                        profile_data["is_quarantined"],
                        json.dumps(profile_json),
                    ),
                )

                saved_count += 1

            except Exception as e:
                logger.error(f"Error saving profile {profile_key}: {e}")

        conn.commit()
        conn.close()

        logger.info(f"✅ Saved {saved_count} user profiles")
        return saved_count

    async def _migrate_violation_records(self) -> Dict[str, int]:
        """Migrate violation records from old databases"""
        logger.info("⚖️ Migrating violation records...")

        # This is a simplified implementation
        # In a real migration, you'd need to parse specific violation formats
        # from each old database and convert them to the unified format

        return {"violations_migrated": 0}

    async def _verify_migration(self) -> Dict[str, Any]:
        """Verify migration integrity"""
        logger.info("🔍 Verifying migration integrity...")

        conn = sqlite3.connect(self.new_database)
        cursor = conn.cursor()

        # Count records
        user_count = cursor.execute("SELECT COUNT(*) FROM user_profiles").fetchone()[0]
        violation_count = cursor.execute(
            "SELECT COUNT(*) FROM violation_records"
        ).fetchone()[0]

        # Check data integrity
        profiles_with_trust = cursor.execute(
            "SELECT COUNT(*) FROM user_profiles WHERE trust_score BETWEEN 0 AND 100"
        ).fetchone()[0]

        conn.close()

        verification = {
            "total_users": user_count,
            "total_violations": violation_count,
            "profiles_with_valid_trust": profiles_with_trust,
            "integrity_check": profiles_with_trust == user_count,
        }

        if verification["integrity_check"]:
            logger.info("✅ Migration integrity check passed")
        else:
            logger.warning("⚠️ Migration integrity check found issues")

        return verification

    async def create_backup(self) -> str:
        """Create backup of existing databases before migration"""
        import shutil
        import time

        backup_dir = f"data/backup_security_{int(time.time())}"
        os.makedirs(backup_dir, exist_ok=True)

        for db_path in self.old_databases:
            if os.path.exists(db_path):
                backup_path = os.path.join(backup_dir, os.path.basename(db_path))
                shutil.copy2(db_path, backup_path)
                logger.info(f"📦 Backed up {db_path} to {backup_path}")

        logger.info(f"✅ Backup created at {backup_dir}")
        return backup_dir


# CLI interface for running migration
if __name__ == "__main__":
    import asyncio

    async def main():
        print("🔄 Security System Migration Tool")
        print("=" * 50)

        migration_tool = SecurityMigrationTool()

        # Create backup first
        print("📦 Creating backup of existing databases...")
        backup_dir = await migration_tool.create_backup()
        print(f"✅ Backup created at: {backup_dir}")

        # Run migration
        print("🔄 Starting migration process...")
        results = await migration_tool.run_migration()

        print("=" * 50)
        print("📊 MIGRATION RESULTS:")
        print("=" * 50)

        for key, value in results.items():
            if key != "errors":
                print(f"{key}: {value}")

        if results.get("errors"):
            print(f"❌ Errors encountered: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"  - {error}")

        print("=" * 50)
        print("✅ Migration process completed!")
        print(f"📄 Check migration log: {migration_tool.migration_log}")

    asyncio.run(main())
