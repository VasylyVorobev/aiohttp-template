from enum import Enum


class RoomChoice(Enum):
    PERSONAL = "Personal"
    GROUP = "Group"


class MessageType(Enum):
    TEXT = "Text"
    IMAGE = "Image"
