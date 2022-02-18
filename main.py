from aiohttp import web


async def index(request):
    return web.Response(text="Welcome home!")


async def my_web_app():
    app = web.Application()
    app.router.add_get('/', index)
    return app
