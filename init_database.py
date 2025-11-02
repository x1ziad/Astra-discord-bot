#!/usr/bin/env python3
"""
Database Initialization Script
Manually creates all required database tables including case_appeals
"""

import sqlite3
from pathlib import Path


def initialize_database():
    """Initialize all database tables"""
    db_path = Path("data/moderation.db")

    # Ensure data directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Initializing database: {db_path}")

    with sqlite3.connect(db_path) as conn:
        # Create moderation_configs table
        print("Creating moderation_configs table...")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS moderation_configs (
                guild_id INTEGER PRIMARY KEY,
                config_json TEXT NOT NULL
            )
            """
        )

        # Create moderation_cases table
        print("Creating moderation_cases table...")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS moderation_cases (
                case_id INTEGER,
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                action TEXT,
                violation TEXT,
                reason TEXT,
                timestamp TEXT,
                expires_at TEXT,
                active INTEGER,
                severity INTEGER,
                evidence_json TEXT,
                notes TEXT,
                appealed INTEGER,
                appeal_status TEXT,
                PRIMARY KEY (guild_id, case_id)
            )
            """
        )

        # Create user_warnings table
        print("Creating user_warnings table...")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_warnings (
                guild_id INTEGER,
                user_id INTEGER,
                warning_count INTEGER DEFAULT 0,
                timeout_count INTEGER DEFAULT 0,
                kick_count INTEGER DEFAULT 0,
                last_violation TEXT,
                PRIMARY KEY (guild_id, user_id)
            )
            """
        )

        # Create user_trust_scores table
        print("Creating user_trust_scores table...")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_trust_scores (
                guild_id INTEGER,
                user_id INTEGER,
                trust_score REAL DEFAULT 100.0,
                last_updated TEXT,
                PRIMARY KEY (guild_id, user_id)
            )
            """
        )

        # Create case_appeals table (NEW)
        print("Creating case_appeals table...")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS case_appeals (
                appeal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER,
                guild_id INTEGER,
                user_id INTEGER,
                reason TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                requires_multi_admin INTEGER DEFAULT 0,
                admin_approvals TEXT DEFAULT '[]',
                admin_denials TEXT DEFAULT '[]',
                final_decision_by INTEGER,
                final_decision_at TEXT,
                final_decision_reason TEXT,
                FOREIGN KEY (guild_id, case_id) REFERENCES moderation_cases(guild_id, case_id)
            )
            """
        )

        # Create indices for performance
        print("Creating indices...")
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_cases_guild_user 
            ON moderation_cases(guild_id, user_id)
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_cases_timestamp 
            ON moderation_cases(timestamp)
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_appeals_guild_user
            ON case_appeals(guild_id, user_id)
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_appeals_status
            ON case_appeals(status)
            """
        )

        conn.commit()

    print("\n✅ Database initialization complete!")

    # Verify tables exist
    print("\nVerifying tables...")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = [
            "moderation_configs",
            "moderation_cases",
            "user_warnings",
            "user_trust_scores",
            "case_appeals",
        ]

        print(f"\nFound {len(tables)} tables:")
        for table in tables:
            status = "✅" if table in expected_tables else "⚠️"
            print(f"  {status} {table}")

        # Verify case_appeals structure
        if "case_appeals" in tables:
            print("\n✅ case_appeals table structure:")
            cursor = conn.execute("PRAGMA table_info(case_appeals)")
            for row in cursor.fetchall():
                col_id, col_name, col_type, not_null, default, pk = row
                print(f"  - {col_name} ({col_type}){' PRIMARY KEY' if pk else ''}")


if __name__ == "__main__":
    print("=" * 80)
    print("ASTRA BOT - DATABASE INITIALIZATION")
    print("=" * 80)
    initialize_database()
    print("\n" + "=" * 80)
    print("Database is ready! Run test_appeal_system.py to verify.")
    print("=" * 80)
