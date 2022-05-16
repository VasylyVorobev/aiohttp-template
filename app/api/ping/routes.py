import typing

if typing.TYPE_CHECKING:
    from main import Application


def setup_routes(app: "Application"):
    from . import views

    app.router.add_view("/ping.health_check", views.PingView)
