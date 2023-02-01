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
import time
from session_lambda import session, set_session_data, get_session_data

@session
def lambda_handler(event, context):
    print(get_session_data())
    set_session_data((get_session_data() or [])+[str(time.time())])
    return {"headers":{}}

# first client_a call 
response = lambda_handler({'headers':{}}, {})  
# get session id from response (created by the server)
session_id = response.get('headers').get('session-id')
# use session id in subsequent calls
lambda_handler({'headers':{'session-id':session_id}}, {})
lambda_handler({'headers':{'session-id':session_id}}, {})
lambda_handler({'headers':{'session-id':session_id}}, {})

# first client_b call 
lambda_handler({'headers':{}}, {})
```
You should get the following prints:
```
None
['1675291378.118798']
['1675291378.118798']
['1675291378.118798']
None
```
This time using the `update=True` mode:
```
import time
from session_lambda import session, set_session_data, get_session_data

@session(update=True)
def lambda_handler(event, context):
    print(get_session_data())
    set_session_data((get_session_data() or [])+[str(time.time())])
    return {"headers":{}}

# first client_a call 
response = lambda_handler({'headers':{}}, {})  
# get session id from response (created by the server)
session_id = response.get('headers').get('session-id')
# use session id in subsequent calls
lambda_handler({'headers':{'session-id':session_id}}, {})
lambda_handler({'headers':{'session-id':session_id}}, {})
lambda_handler({'headers':{'session-id':session_id}}, {})

# first client_b call 
lambda_handler({'headers':{}}, {})
```
Now you should see:
```
None
['1675291406.785664']
['1675291406.785664', '1675291407.565578']
['1675291406.785664', '1675291407.565578', '1675291408.384397']
None
```

## Features
```
@session(id_key_name='session-id', update=False, ttl=0)
def lambda_handler(event, context):
    ...
```
- `id_key_name` is the expected key name in the `event[headers]`. It is default to `session-id`. It is case-sensitive.
- `update` flag let you decide weather to update the session data each call or just not. It is default to `False`.
- `ttl` is seconds interval for the session to live (since the last update time). By default it is disabled. Any value larger then 0 will enable this feature. Make sure to set the TTL key name in your dynamodb to `ttl`.

## Future Features
- Support Schema validation for session data