import json
from typing import Dict, Tuple
import pytest
from session_lambda.session import _session
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

def test_session_decorator_ttl(dynamodb_table_name):    
    use_store(DynamoDBStore(dynamodb_table_name))
    @session(ttl=10)
    def lambda_handler(event: Dict, context: Dict):        
        set_session_data(data="hello world")
        return {}
    lambda_handler({'headers':{"session-id": "1"}}, {})
    
    item = _session._store.get('1', return_item=True)
    assert 'ttl' in item
    
def test_session_decorator_id_key_name(dynamodb_table_name):    
    use_store(DynamoDBStore(dynamodb_table_name))
    @session(id_key_name="custom-session-id")
    def lambda_handler(event: Dict, context: Dict):        
        session_data = get_session_data()
        set_session_data(data="hello world")
        return session_data
    lambda_handler({'headers':{"custom-session-id": "1"}}, {})
    assert "hello world" == lambda_handler({'headers':{"custom-session-id": "1"}}, {})

def test_session_decorator_update(dynamodb_table_name):    
    use_store(DynamoDBStore(dynamodb_table_name))
    @session(update=True)
    def lambda_handler(event: Dict, context: Dict):        
        session_data = get_session_data()
        session_data = session_data or 0
        session_data+=1
        set_session_data(data=session_data)
        return session_data
    assert 1 == lambda_handler({'headers':{"session-id": "1"}}, {})
    assert 2 == lambda_handler({'headers':{"session-id": "1"}}, {})
    

def test_session_decorator_id_in_header(dynamodb_table_name):    
    use_store(DynamoDBStore(dynamodb_table_name))
    @session(return_session_id_in_header=True)
    def lambda_handler(event: Dict, context: Dict):        
        set_session_data(data={})
        return {'headers':{}}
    response = lambda_handler({'headers':{"session-id": "1"}}, {})
    assert "1" == response.get('headers').get('session-id')
    
    @session(return_session_id_in_header=False)
    def lambda_handler(event: Dict, context: Dict):        
        set_session_data(data={})
        return {'headers':{}}
    response = lambda_handler({'headers':{"session-id": "1"}}, {})
    assert response.get('headers').get('session-id', None) is None