#!/usr/bin/env python3
"""
Setup database - Initialize SQLite database with tables
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import Database
from config.settings import DATABASE_PATH


def main():
    """Initialize database"""
    print(f"Setting up database at: {DATABASE_PATH}")

    # Create database instance
    db = Database()

    # Create tables
    db.create_tables()

    print("✓ Database tables created successfully")
    print(f"✓ Database ready at: {DATABASE_PATH}")

    db.close()


if __name__ == '__main__':
    main()