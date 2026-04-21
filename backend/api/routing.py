from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/vessels/", consumers.VesselConsumer.as_asgi()),
]
