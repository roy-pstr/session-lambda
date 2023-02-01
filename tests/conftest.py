import os
from pathlib import Path
import pytest
from moto import mock_dynamodb
import boto3

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

@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture(scope="session")
def TABLE_NAME():
    return "session-lambda-test-table"

@pytest.fixture(scope="function")
def dynamodb_table_name(aws_credentials, TABLE_NAME):
    with mock_dynamodb():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "key", "AttributeType": "S"},
            ],
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "key", "KeyType": "HASH"},
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        yield TABLE_NAME
