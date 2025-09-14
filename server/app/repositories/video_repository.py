"""
Video repository backed by DynamoDB.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.dynamodb_client import DynamoDBClient


class VideoRepository:
    def __init__(self, ddb: Optional[DynamoDBClient] = None) -> None:
        self._ddb = ddb or DynamoDBClient()

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
        # Get QUT username from settings (fixed AWS account username)
        from app.core.config import get_settings
        settings = get_settings()
        qut_username = settings.QUT_USERNAME
        
        # Create composite sort key: owner_username#video_id
        sort_key = f"{owner_username}#{video_id}"
        
        item: Dict[str, Any] = {
            "qut-username": qut_username,    # Partition Key (fixed QUT account)
            "sort-key": sort_key,            # Sort Key (owner_username#video_id)
            "video_id": video_id,            
            "filename": filename,
            "s3_key": s3_key,
            "s3_bucket": s3_bucket,
            "file_type": file_type,
            "created_at": created_at or datetime.now().isoformat(),
            "status": status,
            "owner_username": owner_username,  # App user identifier
        }
        self._ddb.put_video(item)
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
        return self._ddb.get_video(video_id, owner_username)

    def list_by_owner(self, owner_username: str, limit: int = 100, last_key: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resp = self._ddb.query_videos_by_owner(owner_username, limit=limit, last_evaluated_key=last_key)
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
        self._ddb.delete_video(video_id, owner_username)

    def update_fields(self, video_id: str, fields: Dict[str, Any], owner_username: str) -> Dict[str, Any]:
        if not fields:
            current = self._ddb.get_video(video_id, owner_username)
            return current or {}
        update_expr_parts: List[str] = []
        expr_vals: Dict[str, Any] = {}
        for key, value in fields.items():
            update_expr_parts.append(f"#{key} = :{key}")
            expr_vals[f":{key}"] = value
        update_expression = "SET " + ", ".join(update_expr_parts)
        expression_names = {f"#{k}": k for k in fields.keys()}
        result = self._ddb.videos_table.update_item(
            Key={"qut-username": self._ddb.qut_username, "sort-key": f"{owner_username}#{video_id}"},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expr_vals,
            ExpressionAttributeNames=expression_names,
            ReturnValues="ALL_NEW",
        )
        return result.get("Attributes", {})


