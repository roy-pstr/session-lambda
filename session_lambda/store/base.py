from abc import ABC, abstractmethod
import secrets

class StoreBase(ABC):
    """
    An interface for a key/value session store.
    """
    def __init__(self, store) -> None:
        self._store = store
        self._validate_store()
    
    def generate_key(self):
        # https://docs.python.org/3/library/secrets.html
        return secrets.token_urlsafe(32)
    
    @abstractmethod
    def _validate_store(self):
        ...
        
    @abstractmethod
    def get(self, key):
        ...
    
    @abstractmethod
    def put(self, key, value, ttl=0):
        ...