from datetime import datetime
from typing import Optional
from uuid import uuid4

from api.db import db
from sqlalchemy.dialects.postgresql import UUID

from .enums import RoomChoice, MessageType


class ProfileClient(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True, index=True)
    profile_id = db.Column(
        UUID,
        unique=True,
        index=True,
        default=uuid4
    )

    def __init__(self, **kw):
        super().__init__(**kw)
        self._message: Optional["Message"] = None
        self._rooms: set[Room] = set()

    def to_dc(self) -> dict:
        return {
            **self.__values__,
            "profile_id": str(self.profile_id)
        }

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

    @property
    def rooms(self):
        return self._rooms


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(
        UUID,
        unique=True,
        index=True,
        default=uuid4
    )
    name = db.Column(db.Unicode(length=255), nullable=True)
    is_open = db.Column(db.Boolean, default=True)
    room_type = db.Column(db.Enum(RoomChoice), default=RoomChoice.PERSONAL)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._messages_info: Optional["Message"] = None
        self._profiles: list[ProfileClient] = list()

    def to_dc(self) -> dict:
        data = {
            **self.__values__,
            "room_type": self.room_type.value,
            "id": str(self.id)
        }
        return data

    @property
    def messages_info(self) -> Optional["Message"]:
        return self

    @messages_info.setter
    def messages_info(self, message: Optional["Message"]):
        self._messages_info = message

    @property
    def profiles(self) -> list[ProfileClient]:
        return self._profiles

    @profiles.setter
    def profiles(self, value: Optional[ProfileClient]):
        if value is not None:
            self._profiles.append(value)

    def add_profiles(self, profile: ProfileClient):
        self._profiles.append(profile)
        profile._rooms.add(self)


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True, index=True)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    updated = db.Column(db.DateTime, onupdate=datetime.now, index=True)
    message_type = db.Column(db.Enum(MessageType), default=MessageType.TEXT)

    # relationships
    room_id = db.Column(UUID, db.ForeignKey("rooms.id"), nullable=False,)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"))

    def to_dc(self) -> dict:
        return {
            **self.__values__,
            "created_at": self.created_at.isoformat(),
            "updated": self.updated.isoformat() if self.updated else None,
            "message_type": self.message_type.value,
            "room_id": str(self.room_id)
        }


class RoomXProfile(db.Model):
    __tablename__ = "rooms_profiles"
    __table_args__ = (
        db.UniqueConstraint('room_id', 'profile_id'),
    )

    id = db.Column(db.Integer, primary_key=True, index=True)
    room_id = db.Column(UUID, db.ForeignKey("rooms.id"), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)
