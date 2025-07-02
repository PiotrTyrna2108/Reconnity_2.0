"""
This module will contain repository classes that provide data access layer abstraction.
Repository pattern for future implementation of proper data persistence.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any, Dict

# Type variable for generic repository
T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    """Abstract base repository with common CRUD methods"""
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def list(self, filters: Dict[str, Any] = None) -> List[T]:
        """List entities with optional filters"""
        pass
    
    @abstractmethod
    async def update(self, id: Any, data: Dict[str, Any]) -> Optional[T]:
        """Update entity"""
        pass
    
    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete entity"""
        pass
