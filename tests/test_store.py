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

def store_scenario(store):
    assert store.get('foo') == None
    
    store.put('foo', 'bar')
    assert store.get('foo') == 'bar'
    
    store.put('foo', 'bar')
    assert store.get('foo') == 'bar'
    
    store.put('foo', 'bar2')
    assert store.get('foo') == 'bar2'
    
    assert store.get('not_exist') == None

@pytest.mark.parametrize('_Store,store', 
                        [
                            (RuntimeStore, {}),
                            (JSONFileStore, str(currDir/'test_store.json')),
                        ])
def test_local_store(_Store: StoreBase, store):
    store = _Store(store)
    store_scenario(store)

@pytest.mark.parametrize('repeat', range(2))
def test_dynamodb_store(dynamodb_table_name, repeat):
    store = DynamoDBStore(dynamodb_table_name)
    store_scenario(store)