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
    assert store.get('foo') == (None, False)
    store.put('foo', None)
    assert store.get('foo') == (None, True)
    
    store.put('foo', 'bar')
    assert store.get('foo') == ('bar', True)
    
    store.put('foo', 'bar')
    assert store.get('foo') == ('bar', True)
    
    store.put('foo', 'bar2')
    assert store.get('foo') == ('bar2', True)
    
    assert store.get('not_exist') == (None, False)

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

def test_dynamodb_store_ttl(dynamodb_table_name):
    # test ttl with store.put when store is DynamoDBStore
    store = DynamoDBStore(dynamodb_table_name)
    store.put('foo', 'bar', ttl=0)
    item, exist = store.get('foo', return_item=True)
    assert 'ttl' not in item
    store.put('foo', 'bar', ttl=1)
    item, exist = store.get('foo', return_item=True)
    assert 'ttl' in item
    first_ttl = item['ttl']
    store.put('foo', 'bar', ttl=10)
    item, exist = store.get('foo', return_item=True)
    second_ttl = item['ttl']
    assert second_ttl > first_ttl
    