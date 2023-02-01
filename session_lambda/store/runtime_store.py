from .base import StoreBase

class RuntimeStore(StoreBase):
    """
    Dictionary-based store for testing purposes.
    """
    def __init__(self, store) -> None:
        super().__init__(store)
    
    def _validate_store(self):
        if not isinstance(self._store, dict):
            raise TypeError("Store must be a dictionary")
        
    def get(self, key):
        return self._store.get(key)
    
    def put(self, key, value, ttl=0):
        self._store[key] = value
        return value