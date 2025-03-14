"""
Database migration script for initializing the database schema.
"""

import logging
from typing import Optional
from sqlalchemy import text
from bot.database.connection import DatabaseManager
from bot.models.database import Base

logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Handles database migrations and schema updates."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def init_db(self) -> bool:
        """Initialize the database schema."""
        try:
            async with self.db_manager.get_session() as session:
                # Create all tables
                await session.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
                await session.execute(text("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\""))
                await session.commit()
                
                # Create tables
                await session.run_sync(Base.metadata.create_all)
                await session.commit()
                
                logger.info("Database schema initialized successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            return False
    
    async def drop_db(self) -> bool:
        """Drop all tables in the database."""
        try:
            async with self.db_manager.get_session() as session:
                await session.run_sync(Base.metadata.drop_all)
                await session.commit()
                
                logger.info("Database schema dropped successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to drop database schema: {e}")
            return False
    
    async def check_schema(self) -> bool:
        """Check if the database schema is up to date."""
        try:
            async with self.db_manager.get_session() as session:
                # Check if all required tables exist
                for table in Base.metadata.tables.values():
                    result = await session.execute(
                        text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table.name}')")
                    )
                    exists = result.scalar()
                    if not exists:
                        logger.warning(f"Table {table.name} is missing")
                        return False
                
                logger.info("Database schema check completed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to check database schema: {e}")
            return False
    
    async def backup_schema(self, backup_file: str) -> bool:
        """Backup the current database schema."""
        try:
            async with self.db_manager.get_session() as session:
                # Get all table definitions
                tables = []
                for table in Base.metadata.tables.values():
                    result = await session.execute(
                        text(f"SELECT pg_get_tabledef('{table.name}')")
                    )
                    tables.append(result.scalar())
                
                # Write to backup file
                with open(backup_file, 'w') as f:
                    f.write('\n\n'.join(tables))
                
                logger.info(f"Database schema backed up to {backup_file}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to backup database schema: {e}")
            return False
    
    async def restore_schema(self, backup_file: str) -> bool:
        """Restore the database schema from a backup file."""
        try:
            async with self.db_manager.get_session() as session:
                # Read backup file
                with open(backup_file, 'r') as f:
                    schema = f.read()
                
                # Execute schema
                await session.execute(text(schema))
                await session.commit()
                
                logger.info(f"Database schema restored from {backup_file}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to restore database schema: {e}")
            return False

async def run_migrations(db_manager: Optional[DatabaseManager] = None) -> bool:
    """Run database migrations."""
    if db_manager is None:
        db_manager = DatabaseManager()
    
    migrator = DatabaseMigrator(db_manager)
    
    # Check if schema exists
    if not await migrator.check_schema():
        logger.info("Initializing database schema...")
        return await migrator.init_db()
    
    return True 