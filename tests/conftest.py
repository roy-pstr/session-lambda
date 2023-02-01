import os
from pathlib import Path
import pytest

currDir = Path(__file__).resolve().parent
TEST_STORE_JSON_FILE_PATH = str(currDir/'test_store.json')

@pytest.fixture(autouse=True, scope='session')
def session_setup_teardown():
    # SETUP
    print("setup")
    with open(TEST_STORE_JSON_FILE_PATH, "w") as f:
        f.write("{}")
    
    yield
    
    # TEARDOWN
    print("teardown")
    os.remove(TEST_STORE_JSON_FILE_PATH)
    