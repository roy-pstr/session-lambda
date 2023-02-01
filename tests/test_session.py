import json
from typing import Dict, Tuple
import pytest
from session_lambda import session, use_store, RuntimeStore,DynamoDBStore, set_session_data, get_session_data
from session_lambda import SessionStoreNotSet, SessionDataNotSet
def test_session_store_not_set():
    @session
    def lambda_handler(event: Dict, context: Dict) -> Tuple[Dict, Dict]:
        return
    with pytest.raises(SessionStoreNotSet):
        lambda_handler({'headers':{"session-id": ""}}, {})

def test_session_state_not_set():
    use_store(RuntimeStore({}))
    @session
    def lambda_handler(event: Dict, context: Dict):
        response ={
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            }}
        # set_session_data(data="hello world")      
        return response
    with pytest.raises(SessionDataNotSet):
        response = lambda_handler({'headers':{"session-id": "1"}}, {})

def test_session_decorator(dynamodb_table_name):    
    use_store(DynamoDBStore(dynamodb_table_name))
    @session
    def lambda_handler(event: Dict, context: Dict):
        
        session_data = get_session_data()
        if session_data is not None:
            msg = f"Session data exist in store: {session_data}"
        else:
            msg = "Session data did not exist in store"

        response ={
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({
                "message": msg
            })}
        
        set_session_data(data="hello world")
        
        return response
    
    response = lambda_handler({'headers':{"session-id": "1"}}, {})
    assert  json.loads(response.get('body')).get('message')== "Session data did not exist in store"
    
    response = lambda_handler({'headers':{"session-id": "2"}}, {})
    assert  json.loads(response.get('body')).get('message')== "Session data did not exist in store"

    response = lambda_handler({'headers':{"session-id": "1"}}, {})
    assert  json.loads(response.get('body')).get('message')== "Session data exist in store: hello world"