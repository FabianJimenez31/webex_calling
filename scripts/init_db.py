#!/usr/bin/env python
"""
Initialize database schema
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main function to initialize database"""
    logger.info("Initializing database...")

    try:
        init_db()
        logger.info("✅ Database initialized successfully!")
        logger.info("Tables created:")
        logger.info("  - call_detail_records")
        logger.info("  - call_journeys")
        logger.info("  - users")
        logger.info("  - alerts")

    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
