"""
MILO AI Backend - MySQL Setup and Migration Utility

Runs database verification, creates 'milo_db' if it does not exist,
and initializes all SQLAlchemy ORM tables.
"""

import asyncio
import sys
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("milo_mysql_setup")


async def main():
    print("=" * 60)
    print("🐬 MILO AI Backend — MySQL Initialization")
    print("=" * 60)

    from app.config import settings
    from app.db.database import engine, init_db, _is_mysql
    from app.db.models import Base

    print(f"📡 Database URL: {settings.database_url}")
    print(f"🔧 Dialect: {'MySQL' if _is_mysql else 'Other'}")

    try:
        print("\n⏳ Initializing database and tables...")
        await init_db()
        print("✅ Database & tables successfully created/verified!")

        # List all created tables
        async with engine.connect() as conn:
            def get_tables(sync_conn):
                from sqlalchemy import inspect
                inspector = inspect(sync_conn)
                return inspector.get_table_names()

            table_names = await conn.run_sync(get_tables)
            print(f"\n📋 Registered Tables ({len(table_names)} found):")
            for t in sorted(table_names):
                print(f"   • {t}")

        print("\n🎉 MySQL database is ready for MILO!")
    except Exception as e:
        print(f"\n❌ Failed to initialize MySQL database: {e}")
        print("\n💡 Tips:")
        print("   1. Pastikan XAMPP atau Laragon sudah di-Start (Apache & MySQL).")
        print("   2. Pastikan package driver sudah terpasang: uv add aiomysql pymysql cryptography")
        print("   3. Periksa kecocokan user/password di file .env (default XAMPP/Laragon: root tanpa password).")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
