import json
from typing import Dict, Tuple
import pytest
from session_lambda.session import _session
from session_lambda import session, use_store, RuntimeStore,DynamoDBStore, set_session_data, get_session_data, use_session_id_from_seed
from session_lambda import SessionStoreNotSet
def test_session_store_not_set():
    @session
    def lambda_handler(event: Dict, context: Dict) -> Tuple[Dict, Dict]:
        return
    with pytest.raises(SessionStoreNotSet):
        lambda_handler({}, {})

def test_session_id_in_response_headers():
    use_store(RuntimeStore({}))
    @session
    def lambda_handler(event: Dict, context: Dict):
        response ={
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            }
            }
        return response
    response = lambda_handler({}, {})
    assert 'session-id' in response.get('headers')
    
def test_session_id_in_response_headers_as_str():
    use_store(RuntimeStore({}))
    @session
    def lambda_handler(event: Dict, context: Dict):
        response ={
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                }
            }
        return json.dumps(response)
    response = lambda_handler({}, {})
    assert 'session-id' in json.loads(response).get('headers')
    
def test_session_decorator(dynamodb_table_name):    
    use_store(DynamoDBStore(dynamodb_table_name))
    @session
    def lambda_handler(event: Dict, context: Dict):
        session_data = get_session_data()
        
        response = {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                },
                "body": session_data
            }
        
        set_session_data(data="hello world")
        return response
    
    response = lambda_handler({}, {})
    assert  response.get('body') is None
    session_id = response.get('headers').get('session-id')

    response = lambda_handler({'headers':{"session-id": session_id}}, {})
    assert  response.get('body') == "hello world"

    response = lambda_handler({'headers':{"session-id": session_id[1:]}}, {})
    assert  response.get('body') is None

def test_session_decorator_with_client_generated_session_id(dynamodb_table_name):    
    use_store(DynamoDBStore(dynamodb_table_name))
    @session
    def lambda_handler(event: Dict, context: Dict):
        session_data = get_session_data()
        response = {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                },
                "body": session_data
            }
        
        set_session_data(data="hello world")
        return response
    
    client_session_id = "1"
    response = lambda_handler({'headers':{"session-id": client_session_id}}, {})
    assert  response.get('body') is None
    session_id = response.get('headers').get('session-id')
    assert session_id == client_session_id
    response = lambda_handler({'headers':{"session-id": client_session_id}}, {})
    assert  response.get('body') == "hello world"
    
def test_session_decorator_ttl(dynamodb_table_name):    
    use_store(DynamoDBStore(dynamodb_table_name))
    @session(ttl=10)
    def lambda_handler(event, context):
        return {'headers':{}}
    
    response = lambda_handler({'headers':{}}, {})
    session_id = response.get('headers').get('session-id')
    item, _ = _session._store.get(session_id, return_item=True)
    assert 'ttl' in item
    
def test_session_decorator_id_key_name(dynamodb_table_name):    
    use_store(DynamoDBStore(dynamodb_table_name))
    @session(id_key_name="custom-session-id")
    def lambda_handler(event: Dict, context: Dict):        
        return {'headers':{}}
    response = lambda_handler({}, {})
    assert 'custom-session-id' in response.get('headers')

def test_session_decorator_update(dynamodb_table_name):    
    use_store(DynamoDBStore(dynamodb_table_name))
    @session(update=True)
    def lambda_handler(event: Dict, context: Dict):        
        session_data = get_session_data()
        session_data = session_data or 0
        session_data+=1
        set_session_data(data=session_data)
        return {'headers':{}, 'body': session_data}
    response = lambda_handler({}, {})
    assert response.get('body') == 1
    session_id = response.get('headers').get('session-id')
    
    response = lambda_handler({'headers':{"session-id": session_id}}, {})
    assert response.get('body') == 2
    
def test_session_decorator_with_seed(dynamodb_table_name):    
    use_store(DynamoDBStore(dynamodb_table_name))
    @session
    def lambda_handler(event: Dict, context: Dict):
        use_session_id_from_seed("seed")
        session_data = get_session_data()
        
        response = {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                },
                "body": session_data
            }
        
        set_session_data(data="hello world")
        return response
    
    response = lambda_handler({}, {})
    assert  response.get('body') is None
    session_id = response.get('headers').get('session-id')
    
    response = lambda_handler({'headers':{"session-id": session_id}}, {})
    assert  response.get('body') == "hello world"

    response = lambda_handler({'headers':{"session-id": session_id[1:]}}, {})
    assert  response.get('body') == "hello world"