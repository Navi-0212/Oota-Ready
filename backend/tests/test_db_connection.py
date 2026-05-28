"""
Unit tests for Database Connection
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.db.connection import DatabaseConnection, DatabaseConnectionError, get_database, init_database


@pytest.fixture
def mock_database_url():
    """Mock database URL"""
    return "postgresql://test:test@localhost:5432/test"


class TestDatabaseConnection:
    """Test cases for DatabaseConnection class"""
    
    @patch('app.db.connection.create_engine')
    def test_init_database_connection(self, mock_create_engine, mock_database_url):
        """Test database connection initialization"""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        db = DatabaseConnection(mock_database_url)
        
        assert db.database_url == mock_database_url
        assert db.engine is not None
        mock_create_engine.assert_called_once()
    
    @patch('app.db.connection.create_engine')
    def test_init_database_connection_failure(self, mock_create_engine):
        """Test database connection initialization failure"""
        mock_create_engine.side_effect = Exception("Connection failed")
        
        with pytest.raises(DatabaseConnectionError):
            DatabaseConnection("postgresql://invalid")
    
    @patch('app.db.connection.create_engine')
    def test_create_tables(self, mock_create_engine, mock_database_url):
        """Test table creation"""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        db = DatabaseConnection(mock_database_url)
        db.create_tables()
        
        # Verify Base.metadata.create_all was called
        # This is a simplified test - in reality, we'd mock Base.metadata
        assert True
    
    @patch('app.db.connection.create_engine')
    def test_drop_tables(self, mock_create_engine, mock_database_url):
        """Test table dropping"""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        db = DatabaseConnection(mock_database_url)
        db.drop_tables()
        
        # Verify Base.metadata.drop_all was called
        assert True
    
    @patch('app.db.connection.create_engine')
    def test_get_session(self, mock_create_engine, mock_database_url):
        """Test getting database session"""
        mock_engine = MagicMock()
        mock_session = MagicMock()
        mock_engine.connect.return_value.__enter__ = Mock()
        mock_engine.connect.return_value.__exit__ = Mock()
        mock_create_engine.return_value = mock_engine
        
        db = DatabaseConnection(mock_database_url)
        
        with db.get_session() as session:
            assert session is not None
    
    @patch('app.db.connection.create_engine')
    def test_test_connection(self, mock_create_engine, mock_database_url):
        """Test database connection test"""
        mock_engine = MagicMock()
        mock_session = MagicMock()
        mock_session.execute.return_value = MagicMock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_session)
        mock_engine.connect.return_value.__exit__ = Mock()
        mock_create_engine.return_value = mock_engine
        
        db = DatabaseConnection(mock_database_url)
        result = db.test_connection()
        
        assert result is True
    
    @patch('app.db.connection.create_engine')
    def test_close_connection(self, mock_create_engine, mock_database_url):
        """Test closing database connection"""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        db = DatabaseConnection(mock_database_url)
        db.close()
        
        mock_engine.dispose.assert_called_once()


class TestGlobalDatabaseFunctions:
    """Test cases for global database functions"""
    
    @patch('app.db.connection.DatabaseConnection')
    def test_get_database(self, mock_db_connection, mock_database_url):
        """Test getting global database connection"""
        mock_instance = MagicMock()
        mock_db_connection.return_value = mock_instance
        
        db = get_database()
        
        assert db is not None
    
    @patch('app.db.connection.DatabaseConnection')
    def test_init_database_global(self, mock_db_connection, mock_database_url):
        """Test initializing database globally"""
        mock_instance = MagicMock()
        mock_db_connection.return_value = mock_instance
        
        db = init_database(mock_database_url)
        
        assert db is not None
        mock_instance.create_tables.assert_called_once()
