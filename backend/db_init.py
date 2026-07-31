"""
Database initialization script.
Run this to create tables and seed initial data.

Usage:
    python db_init.py --init
    python db_init.py --reset (WARNING: drops all data)
"""

import sys
import logging
from database import init_db, drop_all_tables
from models_db import User
from database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with tables"""
    logger.info("Initializing database...")
    success = init_db()
    if success:
        logger.info("✓ Database initialized successfully")
        seed_initial_data()
        return True
    return False

def seed_initial_data():
    """Seed initial data"""
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_exists = db.query(User).filter(User.username == "admin").first()
        if admin_exists:
            logger.info("Admin user already exists, skipping seed")
            return

        # Create admin user
        admin = User(
            user_id="admin-001",
            username="admin",
            email="admin@nostromus.local",
            full_name="Administrator",
            role="admin",
            is_active=True
        )
        db.add(admin)

        # Create viewer user
        viewer = User(
            user_id="viewer-001",
            username="viewer",
            email="viewer@nostromus.local",
            full_name="Security Viewer",
            role="viewer",
            is_active=True
        )
        db.add(viewer)

        db.commit()
        logger.info("✓ Initial data seeded successfully")
    except Exception as e:
        logger.error(f"✗ Failed to seed data: {e}")
        db.rollback()
    finally:
        db.close()

def reset_database():
    """Drop all tables and reinitialize (DANGEROUS!)"""
    logger.warning("⚠ WARNING: This will drop all data!")
    confirm = input("Type 'yes' to confirm: ")
    if confirm.lower() != "yes":
        logger.info("Cancelled")
        return

    logger.warning("Dropping all tables...")
    drop_all_tables()

    logger.info("Reinitializing database...")
    init_database()
    logger.info("✓ Database reset completed")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "--init":
            init_database()
        elif command == "--reset":
            reset_database()
        else:
            print("Usage: python db_init.py [--init|--reset]")
    else:
        print("Usage: python db_init.py [--init|--reset]")
