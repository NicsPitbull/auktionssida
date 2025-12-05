from abc import ABC, abstractmethod
from typing import List, Optional, Any
import sqlite3
from contextlib import contextmanager

class BaseRepository(ABC):
    """Base repository class implementing common database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_non_query(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT, UPDATE, DELETE and return affected rows or lastrowid"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
    
    @abstractmethod
    def get_all(self) -> List[Any]:
        """Get all records"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Any]:
        """Get record by ID"""
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> int:
        """Create new record"""
        pass
    
    @abstractmethod
    def update(self, id: int, **kwargs) -> bool:
        """Update existing record"""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete record by ID"""
        pass
