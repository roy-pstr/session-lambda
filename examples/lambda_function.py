from pathlib import Path
import sys
rootDir = Path(__file__).resolve().parent.parent
sys.path.append(str(rootDir))

import time
from session_lambda import session, set_session_data, get_session_data

@session
def lambda_handler(event, context):
    print(get_session_data())
    set_session_data((get_session_data() or 0)+1)
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