import os
from .session import session, use_store, set_session_data, get_session_data, SessionStoreNotSet, use_session_id_from_seed
from .store import RuntimeStore, JSONFileStore, DynamoDBStore

from typing import Optional
def init_session_store(
    dynamodb_table_name: Optional[str]=os.getenv("SESSION_LAMBDA_DYNAMODB_TABLE_NAME", None), 
    file_path: Optional[str] = None, 
    runtime: Optional[dict] = None):
    
    if runtime is not None:
        store = RuntimeStore(store=runtime)
        use_store(store)
    
    elif file_path is not None:
        store = JSONFileStore(file_path)
        use_store(store)
    
    elif dynamodb_table_name is not None:
        store = DynamoDBStore(dynamodb_table_name)
        use_store(store)
    
    else:
        raise ValueError("No store is set")

try:
    init_session_store()
except ValueError:
    pass