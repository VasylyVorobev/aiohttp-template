from typing import Optional
from uuid import UUID

from pydantic import BaseModel, root_validator, Field, PositiveInt

from api.chat.enums import RoomChoice, MessageType


class CreateConversation(BaseModel):
    room_type: RoomChoice
    profiles_id: list[UUID]
    name: Optional[str] = None
    message: Optional[str] = None

    @root_validator
    def check_sum(cls, values: dict) -> dict:
        if values.get("room_type") == RoomChoice.PERSONAL:
            if len(values.get("profiles_id")) != 2:
                raise ValueError("There should be two profiles in the personal room")
        return values


class GetConversation(BaseModel):
    room_id: UUID
    limit: PositiveInt
    offset: PositiveInt


class GetConversations(BaseModel):
    limit: PositiveInt
    offset: int = Field(ge=0)


class NewMessage(BaseModel):
    message: str
    room_id: UUID
    message_type: MessageType
