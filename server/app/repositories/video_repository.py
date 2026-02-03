"""
Video repository backed by DynamoDB.
"""

import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import get_settings


class VideoRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self.qut_username = settings.QUT_USERNAME
        session = boto3.session.Session(region_name=settings.AWS_REGION)
        self._ddb = session.resource("dynamodb", region_name=settings.AWS_REGION)
        self.videos_table = self._ddb.Table(settings.DDB_VIDEOS_TABLE)

    def save_metadata(
        self,
        *,
        video_id: str,
        filename: str,
        s3_key: str,
        s3_bucket: str,
        file_type: str,
        owner_username: str,
        created_at: Optional[str] = None,
        status: str = "uploaded",
    ) -> str:
        # Create composite sort key: owner_username#video_id
        sort_key = f"{owner_username}#{video_id}"
        
        item: Dict[str, Any] = {
            "qut-username": self.qut_username,    # Partition Key (fixed QUT account)
            "sort-key": sort_key,                 # Sort Key (owner_username#video_id)
            "video_id": video_id,            
            "filename": filename,
            "s3_key": s3_key,
            "s3_bucket": s3_bucket,
            "file_type": file_type,
            "created_at": created_at or datetime.now().isoformat(),
            "status": status,
            "owner_username": owner_username,  # App user identifier
        }
        self.videos_table.put_item(Item=item)
        return video_id

    def save_transcript_data(
        self,
        *,
        video_id: str,
        transcript_text: str,
        summary: str,
        segments_count: int,
        total_characters: int,
        total_words: int,
        owner_username: str,
        transcript_s3_key: Optional[str] = None,
        transcript_text_s3_key: Optional[str] = None,
        transcript_metadata_s3_key: Optional[str] = None,
        audio_path: Optional[str] = None,
    ) -> None:
        """Save transcript data to the same video record"""
        update_fields = {
            "transcript": transcript_text,
            "summary": summary,
            "segments_count": segments_count,
            "total_characters": total_characters,
            "total_words": total_words,
        }
        if transcript_s3_key:
            update_fields["transcript_s3_key"] = transcript_s3_key
        if transcript_text_s3_key:
            update_fields["transcript_text_s3_key"] = transcript_text_s3_key
        if transcript_metadata_s3_key:
            update_fields["transcript_metadata_s3_key"] = transcript_metadata_s3_key
        if audio_path:
            update_fields["audio_path"] = audio_path
        
        self.update_fields(video_id, update_fields, owner_username)

    def get(self, video_id: str, owner_username: str) -> Optional[Dict[str, Any]]:
        sort_key = f"{owner_username}#{video_id}"
        resp = self.videos_table.get_item(
            Key={"qut-username": self.qut_username, "sort-key": sort_key}
        )
        return resp.get("Item")

    def list_by_owner(self, owner_username: str, limit: int = 100, last_key: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "KeyConditionExpression": Key("qut-username").eq(self.qut_username) & Key("sort-key").begins_with(f"{owner_username}#"),
            "ScanIndexForward": False,  # Sort by sort-key descending
            "Limit": limit,
        }
        if last_key:
            params["ExclusiveStartKey"] = last_key
        
        resp = self.videos_table.query(**params)
        items = resp.get("Items", [])
        return {
            "items": [
                {
                    "video_id": it.get("video_id"),
                    "filename": it.get("filename"),
                    "summary": it.get("summary"),
                    "transcript": it.get("transcript"),
                    "created_at": it.get("created_at"),
                    "status": it.get("status", "uploaded"),
                    "file_type": it.get("file_type"),
                    "s3_key": it.get("s3_key"),
                    "s3_bucket": it.get("s3_bucket"),
                }
                for it in items
            ],
            "last_evaluated_key": resp.get("LastEvaluatedKey"),
        }

    def delete(self, video_id: str, owner_username: str) -> None:
        sort_key = f"{owner_username}#{video_id}"
        self.videos_table.delete_item(
            Key={"qut-username": self.qut_username, "sort-key": sort_key}
        )

    def update_fields(self, video_id: str, fields: Dict[str, Any], owner_username: str) -> Dict[str, Any]:
        if not fields:
            current = self.get(video_id, owner_username)
            return current or {}
        
        update_expr_parts: List[str] = []
        expr_vals: Dict[str, Any] = {}
        for key, value in fields.items():
            update_expr_parts.append(f"#{key} = :{key}")
            expr_vals[f":{key}"] = value
        
        update_expression = "SET " + ", ".join(update_expr_parts)
        expression_names = {f"#{k}": k for k in fields.keys()}
        sort_key = f"{owner_username}#{video_id}"
        
        result = self.videos_table.update_item(
            Key={"qut-username": self.qut_username, "sort-key": sort_key},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expr_vals,
            ExpressionAttributeNames=expression_names,
            ReturnValues="ALL_NEW",
        )
        return result.get("Attributes", {})


