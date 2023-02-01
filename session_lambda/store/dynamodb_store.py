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
    _ttl: str = 'ttl'
    
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
    
    def get(self, key, return_item=False):
        table = self._table()
        response = table.get_item(
            Key={DynamoDBStore._id: key},
        )
        if return_item:
            return response.get('Item',{})
        return response.get('Item',{}).get(DynamoDBStore._value)
    
    def put(self, key, value, ttl=0):
        table = self._table()
        update_expression = 'ADD #counter :increment SET #value = :value, #created_at = if_not_exists(#created_at, :now)'
        ttl_value = int(time.time())+ttl
        if ttl>0:
            update_expression += ', #ttl = :ttl'
        response = table.update_item(
            Key={DynamoDBStore._id: key},
            ReturnValues='ALL_OLD',
            UpdateExpression=update_expression,
            ExpressionAttributeNames={
                '#value': DynamoDBStore._value,
                '#counter': 'access_counter',
                '#created_at': 'created_at',
                '#ttl': DynamoDBStore._ttl
            },
            ExpressionAttributeValues={
                ':increment': 1,
                ':value': value,
                ':now': int(time.time()),
                ':ttl': ttl_value,
            }
            )
        return response.get('Attributes')