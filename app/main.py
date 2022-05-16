import os
from typing import Optional

from aiohttp.web import (
    Application as AiohttpApplication,
    View as AiohttpView,
    Request as AiohttpRequest,
)
from aiohttp_apispec import setup_aiohttp_apispec
import socketio

from logger import setup_logging
from routes import setup_routes
from api.db import setup_db, close_db
from middlewares import setup_middlewares
from store import setup_store, Store


class Application(AiohttpApplication):
    store: Optional[Store] = None


mgr = socketio.AsyncRedisManager(os.environ.get("REDIS_URL"))

sio = socketio.AsyncServer(
    async_mode='aiohttp',
    client_manager=mgr,
)
app = Application()
sio.attach(app)


class Request(AiohttpRequest):

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


async def setup_app() -> Application:

    setup_logging(app)
    app.on_startup.append(setup_db)
    app.on_cleanup.append(close_db)
    setup_routes(app)
    setup_aiohttp_apispec(app, title="Chat", url="/docs/json", swagger_path="/docs")

    setup_middlewares(app)
    setup_store(app)

    return app
