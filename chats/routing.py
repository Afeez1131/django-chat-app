from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from .asgi import application
from channel_app.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": application,
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})
