from main import View

from aiohttp_apispec import docs, response_schema
from aiohttp.web import json_response

from .schema import PingSchema


class PingView(View):
    @docs(summary="Health check")
    @response_schema(PingSchema)
    async def get(self):
        return json_response({"detail": True})
