from abc import ABC, abstractmethod
from typing import Any, Tuple

class StoreBase(ABC):
    """
    An interface for a key/value session store.
    """
    def __init__(self, store) -> None:
        self._store = store
        self._validate_store()
    
    
    @abstractmethod
    def _validate_store(self):
        ...
        
    @abstractmethod
    def get(self, key) -> Tuple[Any, bool]:
        ...
    
    @abstractmethod
    def put(self, key, value, ttl=0):
        ...