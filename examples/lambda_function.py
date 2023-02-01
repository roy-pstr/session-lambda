from pathlib import Path
import sys
rootDir = Path(__file__).resolve().parent.parent
sys.path.append(str(rootDir))

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