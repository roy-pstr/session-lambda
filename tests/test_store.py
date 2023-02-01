from pathlib import Path
import pytest

from session_lambda.store.base import StoreBase
from session_lambda.store import RuntimeStore
from session_lambda.store import JSONFileStore
from session_lambda.store import DynamoDBStore

currDir = Path(__file__).resolve().parent

def test_store_base():
    with pytest.raises(TypeError):
        store = StoreBase()

@pytest.mark.parametrize('_Store,store', 
                        [
                            (RuntimeStore, {}),
                            (JSONFileStore, str(currDir/'test_store.json')),
                            (DynamoDBStore, 'session-lambda'),
                        ])
def test_any_store(_Store: StoreBase, store):
    store = _Store(store)
    store.put('foo', 'bar')
    assert store.get('foo') == 'bar'
    
    store.put('foo', 'bar')
    assert store.get('foo') == 'bar'
    
    store.put('foo', 'bar2')
    assert store.get('foo') == 'bar2'
    
    assert store.get('not_exist') == None