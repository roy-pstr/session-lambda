# Session Lambda
A simple way to manage sessions for AWS Lambdas

## Install
```
pip install session-lambda
```

## Example
Set `SESSION_LAMBDA_DYNAMODB_TABLE_NAME` env var:
```
export SESSION_LAMBDA_DYNAMODB_TABLE_NAME=<table-name>
```
Run the following python code:
```
import uuid
from session_lambda import session, set_session_data, get_session_data

@session
def lambda_handler(event, context):
    
    session_data = get_session_data()

    # core_logic(event, context, session_data)
        
    set_session_data(data="hello world")
    
    return {"session_data_before": session_data, "session_data_after": get_session_data()}
    
        
session_id_0 = str(uuid.uuid4())
session_id_1 = str(uuid.uuid4())
print(lambda_handler({'headers':{"session-id": session_id_0}}, {}))
print(lambda_handler({'headers':{"session-id": session_id_0}}, {}))
print(lambda_handler({'headers':{"session-id": session_id_1}}, {}))
```
You should get the following prints:
```
{'session_data_before': None, 'session_data_after': 'hello world'}
{'session_data_before': 'hello world', 'session_data_after': 'hello world'}
{'session_data_before': None, 'session_data_after': 'hello world'}
```

## Features
```
@session(id_key_name='session-id', return_session_id_in_header=True, update=False)
def lambda_handler(event, context):
    ...
```
- `id_key_name` is the expected key name in the `event[headers]`. It is default to `session-id`. It is case-sensitive.
- `update` flag let you decide weather to update the session data each call or just not. It is default to `False`.
- `return_session_id_in_header` flag lets you control is the `session-id` is added to the response's headers (if `headers` exists in response). It is default to `True`.

## Future Features
- Support TTL
- Support Schema validation for session data