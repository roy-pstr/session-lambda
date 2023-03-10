import json
from .base import StoreBase

class JSONFileStore(StoreBase):
    """
    JSON File-based store for testing purposes.
    """
    def __init__(self, store) -> None:
        super().__init__(store)
    
    def _validate_store(self):
        if not isinstance(self._store, str):
            raise TypeError("store must be a string")
        try:
            self._data()
        except FileNotFoundError:
            raise ValueError("Store must be a file path")
        except json.decoder.JSONDecodeError:
            raise ValueError("Store must be a valid JSON file")
        except Exception as e:
            raise e
        
    def _data(self):
        with open(self._store, "r") as f:
            return json.load(f)
    
    def get(self, key):
        data = self._data()
        return data.get(key), key in data
    
    def put(self, key, value, ttl=0):
        data = self._data()
        with open(self._store, "w") as f:
            data[key] = value
            json.dump(data, f, indent=4)
        return value