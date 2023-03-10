from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path('ws/<chatroom_name>', consumers.ChatConsumer.as_asgi())
]
