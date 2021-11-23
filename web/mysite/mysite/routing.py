from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from liveapp import consumer


websocket_urlPattern = [
    # In routing.py, "as_asgi()" is required for versions over python 3.6.
    # add ws for prefix.
    path('ws/pollData', consumer.DashConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(websocket_urlPattern))
})
