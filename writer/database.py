"""Abstract base class for database operations."""
from abc import ABC, abstractmethod

class DatabaseWriter(ABC):
    """Abstract base class for database operations."""
    
    @abstractmethod
    def connect(self):
        """Establish connection to the database."""
        pass
    
    @abstractmethod
    def process(self, data):
        """Process and store data in the database."""
        pass
    
    @abstractmethod
    def close(self):
        """Close database connection."""
        pass
