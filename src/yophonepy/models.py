from dataclasses import dataclass
from typing import Any, Dict, Optional, Union


@dataclass
class Sender:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    id: Union[str, int] = ""

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Sender":
        return Sender(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            id=data.get("id", ""),
        )


@dataclass
class Message:
    update_id: int
    bot_id: str
    chat_id: str
    text: str
    sender: Sender

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Message":
        """
        Parse a raw dictionary into a Message object.
        Handles nested sender parsing as well.
        """
        return Message(
            update_id=data.get("update_id", 0),
            bot_id=data.get("bot_id", ""),
            chat_id=data.get("chat_id", ""),
            text=data.get("text", ""),
            sender=Sender.from_dict(data.get("sender", {})),
        )
