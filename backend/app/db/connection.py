"""
Database Connection Module
Handles database connection and session management
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Generator
import os

from .models import Base

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager"""
    
    def __init__(self, database_url: str = None):
        """
        Initialize database connection
        
        Args:
            database_url: Database connection string
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://zomato_user:zomato_pass@localhost:5432/zomato"
        )
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize database engine"""
        db_url = self.database_url
        try:
            kwargs = {
                "pool_pre_ping": True,
                "echo": os.getenv("DEBUG", "false").lower() == "true"
            }
            if "sqlite" not in db_url:
                kwargs["pool_size"] = 10
                kwargs["max_overflow"] = 20
                
            self.engine = create_engine(db_url, **kwargs)
            
            # Test connection to ensure database is reachable
            self.engine.connect().close()
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            logger.info("Database engine initialized successfully")
        except Exception as e:
            # Check if we can gracefully fallback to SQLite
            if "postgresql" in db_url:
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                fallback_path = os.path.join(backend_dir, "zomato.db").replace("\\", "/")
                fallback_url = f"sqlite:///{fallback_path}"
                logger.warning(f"Failed to connect to PostgreSQL ({db_url}): {e}. Falling back to SQLite: {fallback_url}")
                try:
                    self.database_url = fallback_url
                    self.engine = create_engine(
                        fallback_url,
                        echo=os.getenv("DEBUG", "false").lower() == "true"
                    )
                    self.SessionLocal = sessionmaker(
                        autocommit=False,
                        autoflush=False,
                        bind=self.engine
                    )
                    logger.info("Database engine initialized successfully with SQLite fallback")
                    return
                except Exception as ex:
                    logger.error(f"Failed to initialize SQLite fallback: {ex}")
            
            logger.error(f"Failed to initialize database engine: {e}")
            raise DatabaseConnectionError(f"Failed to initialize database: {str(e)}")
    
    def create_tables(self):
        """Create all tables in the database"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise DatabaseConnectionError(f"Failed to create tables: {str(e)}")
    
    def drop_tables(self):
        """Drop all tables in the database"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise DatabaseConnectionError(f"Failed to drop tables: {str(e)}")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session with context manager
        
        Yields:
            Database session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_session_direct(self) -> Session:
        """
        Get database session without context manager
        
        Returns:
            Database session
        """
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """
        Test database connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


class DatabaseConnectionError(Exception):
    """Raised when database connection fails"""
    pass


# Global database connection instance
db_connection: DatabaseConnection = None


def get_database() -> DatabaseConnection:
    """
    Get global database connection instance
    
    Returns:
        Database connection instance
    """
    global db_connection
    if db_connection is None:
        db_connection = DatabaseConnection()
    return db_connection


def init_database(database_url: str = None) -> DatabaseConnection:
    """
    Initialize database connection and create tables
    
    Args:
        database_url: Database connection string
        
    Returns:
        Database connection instance
    """
    global db_connection
    db_connection = DatabaseConnection(database_url)
    db_connection.create_tables()
    return db_connection
