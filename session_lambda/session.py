from dataclasses import dataclass
import json
from typing import Any, Optional
import secrets

class SessionStoreNotSet(Exception):
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
            ttl=0,
        ):
        self.func = func
        self.id_key_name = id_key_name
        self.update = update
        self._initial_session = True
        self._ttl_in_seconds = ttl
        setattr(self, "_state", State(value=None, key=None))
    
    def generate_key(self):
        # https://docs.python.org/3/library/secrets.html
        return secrets.token_urlsafe(32)
    
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
    
    def _get_session_id_from_event(self, event):
        if "headers" in event:
            if self.id_key_name in event["headers"]:
                return event["headers"][self.id_key_name]
        return None
    
    def _pre_handler(self, event, context):
        """
        This set the self.state: key and value
        - key is the session_id
        - value is the session_data
        A session can be in one of the following states:
        1. New session by server
            - session_id is not present in the event
        2. New session by client
            - session_id is present in the event
            - session_id is not present in the store
        3. Existing session
            - session_id is present in the event
            - session_id is present in the store
        """
        initial_session: bool = True
        session_id: Optional[str] = self._get_session_id_from_event(event)
        session_data = None
        
        if session_id is None:
            # session_id is not present in the event -> generate a new session_id
            # this will be the first time accessing the session
            session_id = self.generate_key()
            initial_session = True
        else:
            # session_id was found in the event 
            # check if session_id is present in the store
            session_data, session_exist = self.store.get(session_id)
            if not session_exist:
                # session_id is not present in the store 
                # -> this is client generated session_id
                # this will be the first time accessing the session 
                initial_session = True
                assert session_data is None
            else:
                # session_id is present in the store 
                # -> this is not the first time accessing the session
                initial_session = False
        
        self.state.key=session_id
        self.state.value=session_data
        self._initial_session = initial_session
        
    def _post_handler(self):
        """
        This modify data in store.
        There are two cases in which we will update the store:
        - Initial session (new session)
        - Update session (update=True)
        """
        
        if self._initial_session or self.update:
            self.store.put(key=self.state.key, value=self.state.value, ttl=self._ttl_in_seconds)

    def _set_session_id_in_header(self, response):
        if isinstance(response, dict):
            if "headers" in response:
                response["headers"][self.id_key_name] = self.state.key
            return response
        elif isinstance(response, str):
            try:
                _response = json.loads(response)
                if "headers" in _response:
                    _response["headers"][self.id_key_name] = self.state.key
                    response = json.dumps(_response)
                return response
            except:
                pass
        else:
            return response
                
            
    def __call__(self, event, context):
        self._pre_handler(event, context)
        
        response = self.func(event, context)
        
        # update session id in response's header
        response = self._set_session_id_in_header(response)
        
        self._post_handler()
        
        self._teardown()
        
        return response
        
    def _teardown(self):
        setattr(_session, "_state", State(value=None, key=None))
        

        
def session(
        f=None, 
        id_key_name="session-id", 
        update=False,
        ttl=0,
    ):
    if f is not None:
        return _session(f)
    else:
        def wrapper(f):
            return _session(f, id_key_name, update, ttl)
        return wrapper
    
    
use_store = lambda x: setattr(_session, "_store", x)
get_session_state = lambda: getattr(_session, "_state")
get_session_data = lambda: getattr(_session, "_state").value
set_session_state = lambda x: setattr(_session, "_state", x)
set_session_data = lambda data: setattr(get_session_state(), "value", data)
