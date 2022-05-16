from typing import Optional, TYPE_CHECKING

from sqlalchemy import and_

from store.base import BaseAccessor
from api.chat.models import Room, ProfileClient, Message, RoomXProfile
from api.chat.enums import RoomChoice
from api.db import db

if TYPE_CHECKING:
    from api.socketio_server.schemes import CreateConversation, GetConversation, NewMessage
    from uuid import UUID


class ChatAccessor(BaseAccessor):

    async def create_conversation(self, chat_data: "CreateConversation") -> dict:
        profiles_ids = await self.get_or_create_profiles_clients(chat_data.profiles_id)
        if chat_data.room_type == RoomChoice.PERSONAL:
            if room := await self.profiles_public_room_exists(profiles_ids):
                return {
                    "room": room.to_dc(),
                    "profiles_id": [str(profile_id) for profile_id in chat_data.profiles_id]
                }
        room = await self.create_room(chat_data.room_type.name, chat_data.name)
        await self.create_profiles_room(room.id, profiles_ids)
        return {
            "room": room.to_dc(),
            "profiles_id": [str(profile_id) for profile_id in chat_data.profiles_id]
        }

    async def get_room(self, room_id: "UUID") -> Room:
        return await (
            Room.query
            .where(Room.id == room_id)
            .gino
            .first()
        )

    async def create_personal_room(self, profile_room_id: int):
        pass

    async def profiles_public_room_exists(self, profile_ids: list[int]) -> Optional["Room"]:
        current_profile_room_id = await (
            Room
            .outerjoin(RoomXProfile, Room.id == RoomXProfile.room_id)
            .select()
            .where(
                and_(
                    RoomXProfile.profile_id == profile_ids[0],
                    Room.room_type == RoomChoice.PERSONAL.name
                )
            )
            .gino
            .load(Room.id)
            .all()
        )

        room = await (
            Room
            .outerjoin(RoomXProfile, Room.id == RoomXProfile.room_id)
            .select()
            .where(
                and_(
                    RoomXProfile.profile_id == profile_ids[1],
                    Room.room_type == RoomChoice.PERSONAL.name,
                    Room.id.in_(current_profile_room_id)
                )
            )
            .gino
            .load(Room)
            .first()
        )

        return room

    @staticmethod
    async def create_profiles_room(room_id: "UUID", profiles_ids: list[int]) -> int:
        data = await (
            RoomXProfile
            .insert().gino
            .all(
                [
                    {"room_id": room_id, "profile_id": profile_id}
                    for profile_id in profiles_ids
                ]
            )
        )
        return data

    async def create_room(
            self,
            room_type: "RoomChoice",
            name: Optional[str],
    ) -> Room:
        return await Room.create(room_type=room_type, name=name)

    async def get_or_create_profiles_clients(
            self,
            profile_ids: list["UUID"]
    ) -> list[int]:
        profiles = []
        for profile_id in profile_ids:
            if await self.is_profile_exists(profile_id):
                profile = await self.get_profile_by_profile_id(profile_id)
                profiles.append(profile)
                continue
            profile = await ProfileClient.create(profile_id=profile_id)

            profiles.append(profile.id)
        return profiles

    async def get_profile_by_profile_id(self, profile_id: "UUID") -> Optional[int]:
        profile = await (
            ProfileClient.query
            .where(ProfileClient.profile_id == profile_id)
            .gino
            .load(ProfileClient.id)
            .first()
        )
        return profile

    async def is_profile_exists(self, profile_id: "UUID") -> bool:
        profile_exists = await (
            db.scalar(
                db.exists(
                    ProfileClient.query.where(ProfileClient.profile_id == profile_id)
                )
                .select()
            )
        )
        return profile_exists

    @staticmethod
    async def get_room_profiles(room_id: "UUID") -> list["UUID"]:
        return await (
            ProfileClient
            .outerjoin(RoomXProfile, ProfileClient.id == RoomXProfile.profile_id)
            .outerjoin(Room, Room.id == RoomXProfile.room_id)
            .select()
            .where(Room.id == room_id)
            .gino
            .load(ProfileClient.profile_id)
            .all()
        )

    async def get_conversation(self, room: "GetConversation"):
        if room := await self.get_room(room.room_id):
            return {
                "room": room.to_dc(),
                "profiles": [str(profile_id) for profile_id in await self.get_room_profiles(room.id)]
            }
        return {"error": True, "detail": "The room does not exist"}

    async def get_profile_rooms(self, profile_uuid: "UUID", limit: int, offset: int) -> list[dict]:
        profile_id = await self.get_profile_by_profile_id(profile_uuid)
        rooms_id = await (
            Room
            .outerjoin(RoomXProfile)
            .select()
            .where(RoomXProfile.profile_id == profile_id)
            .limit(limit)
            .offset(offset)
            .gino
            .load(Room.id)
            .all()
        )

        rooms = await (
            Room
            .outerjoin(RoomXProfile)
            .outerjoin(ProfileClient)
            .select()
            .where(
                Room.id.in_(rooms_id)
            )
            .gino
            .load(
                Room.distinct(Room.id)
                .load(
                    add_profiles=ProfileClient.distinct(ProfileClient.id),
                )
            )
            .all()
        )

        res = []
        for room in rooms:
            res.append(
                {
                    **room.to_dc(),
                    "profiles": [profile.to_dc() for profile in room.profiles],
                    "message": []
                }
            )
        return res

    async def get_conversations(self, profile_id: "UUID", limit: int, offset: int) -> list[dict]:
        rooms = await self.get_profile_rooms(profile_id, limit, offset)
        return rooms

    @staticmethod
    async def create_message(
            message: str,
            profile_id: int,
            room_id: "UUID"
    ) -> Message:
        message = await Message.create(
            message=message,
            room_id=room_id,
            profile_id=profile_id
        )
        return message

    async def is_profile_in_room(self, room_id: "UUID", profile_id: "UUID") -> Optional[int]:
        if profile_id := await self.get_profile_by_profile_id(profile_id):
            profile_in_room = await (
                db.scalar(
                    db.exists(
                        RoomXProfile.query.where(
                            and_(
                                RoomXProfile.profile_id == profile_id,
                                RoomXProfile.room_id == room_id
                            )
                        )
                    )
                    .select()
                )
            )
            return profile_id if profile_in_room else None
        return

    async def new_message(self, message_data: "NewMessage", profile_id: "UUID") -> dict:
        if profile_pk := await self.is_profile_in_room(message_data.room_id, profile_id):
            message = await self.create_message(message_data.message, profile_pk, message_data.room_id)
            return message.to_dc()
        return {"error": True, "detail": "There is no such profile in this room"}

    async def get_rooms_id_by_profile_uuid(self, profile_uuid: "UUID") -> list["UUID"]:
        profile_id = await self.get_profile_by_profile_id(profile_uuid)
        return await (
            Room
            .outerjoin(RoomXProfile)
            .select()
            .where(RoomXProfile.profile_id == profile_id)
            .gino
            .load(Room.id)
            .all()
        )
