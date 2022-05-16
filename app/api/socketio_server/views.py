from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import ValidationError

from main import sio
from .schemes import CreateConversation, GetConversation, GetConversations, NewMessage
from .utils import get_token_from_environ, get_profile_id_from_token

if TYPE_CHECKING:
    from main import Application


@sio.event
async def connect(sid, environ):
    token = get_token_from_environ(environ)
    if profile_id := get_profile_id_from_token(token):
        app = environ['aiohttp.request'].app

        rooms_id = await app.store.chat.get_rooms_id_by_profile_uuid(profile_id)
        for room in rooms_id:
            sio.enter_room(sid, str(room))

        await sio.save_session(
            sid,
            {
                "profile_id": profile_id,
                "app": app,
            }
        )
    return {"error": True, "detail": "Authentication failed"}


@sio.event
async def disconnect(sid):
    pass


@sio.event
async def create_conversation(sid, data: dict):
    session = await sio.get_session(sid)
    app: "Application" = session["app"]
    try:
        conversation_data = CreateConversation(**data)
    except ValidationError as e:
        await sio.emit("create_conversation", {"error": True, "detail": e.json()}, room=sid)
    else:
        if UUID(session["profile_id"]) in conversation_data.profiles_id:
            conversation = await (
                app.store.chat
                .create_conversation(conversation_data)
            )

            profile_sids = await app.store.redis.many_get(conversation["profiles_id"])
            room_id = conversation["room"]["id"]
            for profile in profile_sids:
                sio.enter_room(profile, room_id)

            await sio.emit("create_conversation", conversation, room=room_id)
        else:
            await sio.emit(
                "create_conversation",
                {"error": True, "detail": "incorrect profile_id"},
                room=sid
            )


@sio.event
async def get_conversation(sid, data: dict):
    session = await sio.get_session(sid)
    app: "Application" = session["app"]
    try:
        room = GetConversation(**data)
        conversation = await (
            app.store.chat.get_conversation(room)
        )

        sio.enter_room(sid, room.room_id)
        await sio.emit("get_conversation", conversation, room=sid)
    except ValidationError as e:
        await sio.emit("get_conversation", {"error": True, "detail": e.json()}, room=sid)


@sio.event
async def get_conversations(sid, data: dict):
    session = await sio.get_session(sid)
    app: "Application" = session["app"]
    try:
        data = GetConversations(**data)
    except ValidationError as e:
        await sio.emit("get_conversations", {"error": True, "detail": e.json()}, room=sid)
    else:

        profile_id = session["profile_id"]
        conversations = await app.store.chat.get_conversations(profile_id, data.limit, data.offset)
        await sio.emit("get_conversations", conversations, room=sid)


@sio.event
async def new_message(sid, data):
    try:
        data = NewMessage(**data)
    except ValidationError as e:
        await sio.emit("new_message", {"error": True, "detail": e.json()}, room=e)
    else:
        session = await sio.get_session(sid)
        app: "Application" = session["app"]
        profile_id = session["profile_id"]
        message = await app.store.chat.new_message(data, profile_id)

        await sio.emit("new_message", message, room=str(data.room_id))
