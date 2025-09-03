import boto3
from datetime import datetime
import json
import os
from typing import Dict, Any, Optional

from ..core.config import settings

class DynamoDBLogger:
    def __init__(self, table_name: str = settings.DYNAMODB_TABLE_NAME):
        self.table_name = table_name
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.table = self.dynamodb.Table(table_name)
        self.enabled = (settings.AWS_ACCESS_KEY_ID is not None and 
                       settings.AWS_SECRET_ACCESS_KEY is not None)

    def log(self, log_level: str, message: str, context: Optional[Dict[str, Any]] = None) -> bool:
        if not self.enabled:
            return False
            
        item = {
            'timestamp': datetime.utcnow().isoformat(),
            'log_level': log_level,
            'message': message
        }
        if context:
            item['context'] = json.dumps(context, default=str)

        try:
            self.table.put_item(Item=item)
            return True
        except Exception as e:
            print(f'Error logging to DynamoDB: {str(e)}')
            return False

    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> bool:
        return self.log('INFO', message, context)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> bool:
        return self.log('WARNING', message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> bool:
        return self.log('ERROR', message, context)
