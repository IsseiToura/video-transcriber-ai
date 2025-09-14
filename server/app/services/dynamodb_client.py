"""
DynamoDB client for video transcriber application.
"""

import boto3
from boto3.dynamodb.conditions import Key
from typing import Any, Dict, Optional

from app.core.config import get_settings


settings = get_settings()


class DynamoDBClient:
    def __init__(self) -> None:
        self.qut_username = settings.QUT_USERNAME
        session = boto3.session.Session(region_name=settings.AWS_REGION)
        self._ddb = session.resource("dynamodb", region_name=settings.AWS_REGION)
        self.videos_table = self._ddb.Table(settings.DDB_VIDEOS_TABLE)

    def get_video(self, video_id: str, owner_username: str) -> Optional[Dict[str, Any]]:
        sort_key = f"{owner_username}#{video_id}"
        resp = self.videos_table.get_item(Key={"qut-username": self.qut_username, "sort-key": sort_key})
        return resp.get("Item")

    def put_video(self, item: Dict[str, Any]) -> None:
        self.videos_table.put_item(Item=item)

    def delete_video(self, video_id: str, owner_username: str) -> None:
        sort_key = f"{owner_username}#{video_id}"
        self.videos_table.delete_item(Key={"qut-username": self.qut_username, "sort-key": sort_key})

    def query_videos_by_owner(self, owner_username: str, limit: int = 50, last_evaluated_key: Optional[Dict[str, Any]] = None):
        
        params: Dict[str, Any] = {
            "KeyConditionExpression": Key("qut-username").eq(self.qut_username) & Key("sort-key").begins_with(f"{owner_username}#"),
            "ScanIndexForward": False,  # Sort by sort-key descending
            "Limit": limit,
        }
        if last_evaluated_key:
            params["ExclusiveStartKey"] = last_evaluated_key
        return self.videos_table.query(**params)

    def update_video_attributes(self, video_id: str, owner_username: str, update_expression: str, expression_attribute_values: Dict[str, Any]):
        sort_key = f"{owner_username}#{video_id}"
        return self.videos_table.update_item(
            Key={"qut-username": self.qut_username, "sort-key": sort_key},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW",
        )
