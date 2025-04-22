import base64
import os
from typing import Dict, Any


def parse_update(update: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse an incoming update into a readable format.
    """
    try:
        decoded_text = base64.b64decode(update.get('text', '')).decode('utf-8')
        return {
            "update_id": update.get('id'),
            "bot_id": update.get('botId', ''),
            "chat_id": update.get('chatId', ''),
            "text": decoded_text,
            "sender": {
                "first_name": update.get('sender', {}).get('firstName', 'Unknown'),
                "last_name": update.get('sender', {}).get('lastName', ''),
                "id": update.get('sender', {}).get('id', ''),
            },
        }
    except Exception as e:
        print(f"Failed to parse update: {e}")
        return {}


def determine_mime_type(file_path: str) -> str:
    """
    Determine the MIME type of file based on its extension.
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".mp4": "video/mp4",
        ".mpeg": "video/mpeg",
        ".webm": "video/webm",
        ".ogg": "video/ogg",
        ".mov": "video/quicktime",
        ".pdf": "application/pdf",
    }
    return mime_types.get(file_extension, "application/octet-stream")
