from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    type: Optional[str] = None

class ConversationSession(BaseModel):
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    messages: list[Message] = []

class AudioChunk(BaseModel):
    data: bytes
    timestamp: float

class WSMessage(BaseModel):
    type: Literal["audio", "text", "control", "error"]
    data: Optional[str] = None
    session_id: Optional[str] = None