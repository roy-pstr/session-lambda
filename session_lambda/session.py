from dataclasses import dataclass
from typing import Any, Optional

class SessionStoreNotSet(Exception):
    pass

class SessionDataNotSet(Exception):
    pass

@dataclass
class State:
    value: Any = None
    key: str = None

class _session:
    _store = None
    _state: Optional[State] = State()
    
    def __init__(self, 
            func, 
            id_key_name="session-id", 
            update=False,
            return_session_id_in_header=True
        ):
        self.func = func
        self.id_key_name = id_key_name
        self.update = update
        self._first_call = True
        self._return_session_id_in_header=return_session_id_in_header
        setattr(self, "_state", State(value=None, key=None))
        
    @classmethod
    @property
    def store(cls):
        if cls._store is None:
            raise SessionStoreNotSet("Store not set")
        return cls._store 
    
    @classmethod
    @property
    def state(cls):
        return cls._state
    
    def _pre_handler(self, event, context):
        session_id = None
        if "headers" in event:
            if self.id_key_name in event["headers"]:
                session_id = event["headers"][self.id_key_name]
                self.state.key = session_id
                
        if self.state.key is not None:
            self.state.value = self.store.get(self.state.key)
            if self.state.value is not None:
                self._first_call = False
            else:
                self._first_call = True
            
    def _post_handler(self):
        if self.state.value is None:
            raise SessionDataNotSet("Session data is not set")
        
        if self._first_call or self.update:
            self.store.put(key=self.state.key, value=self.state.value)

    def _set_session_id_in_header(self, response):
        if "headers" in response:
            response["headers"][self.id_key_name] = self.state.key
        return response
            
    def __call__(self, event, context):
        self._pre_handler(event, context)
        
        response = self.func(event, context)
        
        # update session id in response's header
        if self._return_session_id_in_header:
            response = self._set_session_id_in_header(response)
        
        self._post_handler()
        
        self._teardown()
        
        return response
        
    def _teardown(self):
        setattr(self, "_state", State(value=None, key=None))

        
def session(
        f=None, 
        id_key_name="session-id", 
        update=False,
        return_session_id_in_header=True
    ):
    if f is not None:
        return _session(f)
    else:
        def wrapper(f):
            return _session(f, id_key_name, update)
        return wrapper
    
    
use_store = lambda x: setattr(_session, "_store", x)
get_session_state = lambda: getattr(_session, "_state")
get_session_data = lambda: getattr(_session, "_state").value
set_session_state = lambda x: setattr(_session, "_state", x)
set_session_data = lambda data: setattr(get_session_state(), "value", data)
