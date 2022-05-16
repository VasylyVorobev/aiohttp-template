from aiohttp.web_app import Application
from api.ping.routes import setup_routes as ping_routes
from api.chat.routes import setup_routes as chat_routes
from api.socketio_server.routes import setup_routes as socketio_routes


def setup_routes(app: Application):
    ping_routes(app)
    chat_routes(app)
    socketio_routes(app)
