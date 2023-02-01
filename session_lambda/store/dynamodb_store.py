import json
import time
import boto3, botocore
from .base import StoreBase

class DynamoDBStore(StoreBase):
    """
    JSON File-based store for testing purposes.
    """
    _id: str = 'key'
    _value: str = 'value'
    def __init__(self, store) -> None:
        super().__init__(store)
    
    def _validate_store(self):
        if not isinstance(self._store, str):
            raise TypeError("store must be a string")
        try:
            table = self._table()
        except Exception as e:
            raise e
        
    def _table(self):
        try:
            table = boto3.resource('dynamodb').Table(self._store)
            table.table_status
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ResourceNotFoundException':
                raise ValueError('Requested table not found')
            else:
                raise error
        return table
    
    def get(self, key):
        table = self._table()
        response = table.get_item(
            Key={DynamoDBStore._id: key},
        )
        return response.get('Item',{}).get(DynamoDBStore._value)
    
    def put(self, key, value):
        table = self._table()
        response = table.update_item(
            Key={DynamoDBStore._id: key},
            ReturnValues='ALL_OLD',
            UpdateExpression=f'ADD #counter :increment SET #value = :value, #created_at = if_not_exists(#created_at, :now)',
            ExpressionAttributeNames={
                '#value': DynamoDBStore._value,
                '#counter': 'access_counter',
                '#created_at': 'created_at',
            },
            ExpressionAttributeValues={
                ':increment': 1,
                ':value': value,
                ':now': int(time.time())
            }
            )
        return response.get('Attributes')