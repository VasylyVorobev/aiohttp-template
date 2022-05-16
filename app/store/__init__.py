import typing

if typing.TYPE_CHECKING:
    from main import Application


class Store:
    def __init__(self, app: "Application"):
        from store.chat.accessor import ChatAccessor
        from store.redis_store.accessor import RedisAccessor

        self.chat = ChatAccessor(app)
        self.redis = RedisAccessor(app)


def setup_store(app: "Application"):
    app.store = Store(app)
