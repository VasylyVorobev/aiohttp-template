from typing import TYPE_CHECKING

from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware

if TYPE_CHECKING:
    from main import Application


def setup_middlewares(app: "Application"):
    app.middlewares.append(validation_middleware)
