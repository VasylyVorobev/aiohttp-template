import typing
from logging import getLogger

if typing.TYPE_CHECKING:
    from main import Application


class BaseAccessor:
    def __init__(self, app: "Application", *args, **kwargs):
        self.app = app
        self._init_()
        self.logger = getLogger("accessor")
        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    def _init_(self) -> None:
        return None

    async def connect(self, app: "Application"):
        return

    async def disconnect(self, app: "Application"):
        return
