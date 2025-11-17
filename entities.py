from sqlmodel import SQLModel, Field
from datetime import datetime

class ChatMessage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nick: str
    cuerpo: str
    creado: datetime = Field(default_factory=datetime.utcnow)
