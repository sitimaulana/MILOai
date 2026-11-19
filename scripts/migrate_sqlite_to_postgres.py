"""
MILO AI - SQLite to PostgreSQL Database Migration Utility

Transfers all records from local milo_dev.db SQLite database
into a remote or local PostgreSQL database (e.g. Supabase, Neon, Railway).

Usage:
    python scripts/migrate_sqlite_to_postgres.py --target-url "postgresql://user:pass@host:5432/milo_db"
"""

import argparse
import json
import logging
import os
import sqlite3
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
logger = logging.getLogger("migration")

SQLITE_PATH = os.path.abspath("milo_dev.db")

TABLES_IN_ORDER = [
    "users",
    "sessions",
    "messages",
    "learning_progress",
    "user_gamification",
    "user_badges",
    "system_log_analytics",
    "evaluation_surveys",
]


def parse_datetime(val):
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except Exception:
        return val


def migrate(sqlite_file: str, pg_url: str):
    if not os.path.exists(sqlite_file):
        logger.error(f"SQLite file not found at: {sqlite_file}")
        sys.exit(1)

    logger.info("=" * 65)
    logger.info("🚀 AI-MILO Database Migration: SQLite -> PostgreSQL")
    logger.info("=" * 65)
    logger.info(f"Source SQLite: {sqlite_file}")
    # Mask password in URL for display
    safe_url = pg_url
    if "@" in safe_url and ":" in safe_url:
        prefix = safe_url.split("@")[0]
        host_part = safe_url.split("@")[1]
        safe_url = f"{prefix.split(':')[0]}:****@{host_part}"
    logger.info(f"Target Postgres: {safe_url}")

    # SQLAlchemy sync engine for migration
    from sqlalchemy import create_engine, text
    from app.db.models import Base

    # Convert asyncpg URL to standard psycopg2 URL if passed
    sync_pg_url = pg_url.replace("postgresql+asyncpg://", "postgresql://")

    try:
        engine = create_engine(sync_pg_url, echo=False)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Connected to PostgreSQL successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        sys.exit(1)

    # 1. Ensure target tables exist
    logger.info("Creating schema and tables in PostgreSQL if not present...")
    Base.metadata.create_all(bind=engine)
    logger.info("Schema verification completed.")

    # 2. Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_file)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    total_migrated = 0

    with engine.begin() as pg_conn:
        for table_name in TABLES_IN_ORDER:
            # Check if source table exists
            sqlite_cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
                (table_name,),
            )
            if not sqlite_cur.fetchone():
                logger.warning(f"Table '{table_name}' does not exist in SQLite, skipping.")
                continue

            # Query all rows from SQLite
            sqlite_cur.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cur.fetchall()
            count = len(rows)

            if count == 0:
                logger.info(f"Table '{table_name}': 0 rows (empty)")
                continue

            # Insert into Postgres
            cols = [col[0] for col in sqlite_cur.description]
            col_names_str = ", ".join(cols)
            placeholders = ", ".join([f":{col}" for col in cols])
            insert_stmt = text(
                f"INSERT INTO {table_name} ({col_names_str}) VALUES ({placeholders}) "
                f"ON CONFLICT DO NOTHING"
            )

            inserted_count = 0
            for row in rows:
                data = dict(row)
                # Handle boolean conversions (SQLite 0/1 -> Python bool)
                if table_name == "users" and "is_active" in data:
                    data["is_active"] = bool(data["is_active"])
                if table_name == "sessions" and "is_active" in data:
                    data["is_active"] = bool(data["is_active"])

                # Handle JSON strings to dict
                for json_col in ("feedback", "extra_meta", "survey_responses", "ueq_scores"):
                    if json_col in data and isinstance(data[json_col], str):
                        try:
                            data[json_col] = json.loads(data[json_col])
                        except Exception:
                            pass

                # Handle datetimes
                for dt_col in ("created_at", "ended_at", "last_login", "last_practice_date", "last_updated", "earned_at"):
                    if dt_col in data and data[dt_col]:
                        data[dt_col] = parse_datetime(data[dt_col])

                try:
                    pg_conn.execute(insert_stmt, data)
                    inserted_count += 1
                except Exception as row_err:
                    logger.warning(f"Row skipped in '{table_name}': {row_err}")

            total_migrated += inserted_count
            logger.info(f"Table '{table_name}': {inserted_count}/{count} rows migrated.")

    sqlite_conn.close()
    logger.info("=" * 65)
    logger.info(f"Migration completed! Total {total_migrated} records transferred.")
    logger.info("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate SQLite data to PostgreSQL for hosting")
    parser.add_argument(
        "--sqlite-file",
        default=SQLITE_PATH,
        help="Path to SQLite database file (default: milo_dev.db)",
    )
    parser.add_argument(
        "--target-url",
        default=os.getenv("DATABASE_URL", ""),
        help="Target PostgreSQL connection string (postgresql://user:pass@host:5432/milo_db)",
    )
    args = parser.parse_args()

    if not args.target_url or "sqlite" in args.target_url:
        print("\n[!] Please specify a valid PostgreSQL connection URL.")
        print('Example: python scripts/migrate_sqlite_to_postgres.py --target-url "postgresql://user:pass@ep-cool-123.supabase.co:5432/postgres"\n')
        sys.exit(1)

    migrate(args.sqlite_file, args.target_url)
