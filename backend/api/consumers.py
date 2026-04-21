from channels.generic.websocket import AsyncWebsocketConsumer
import json

class VesselConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        await self.channel_layer.group_add(
            "vessel_updates",
            self.channel_name
        )

        await self.accept()
        print("WebSocket connected")

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            "vessel_updates",
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def send_vessel_update(self, event):

        vessel = event["vessel"]

        await self.send(text_data=json.dumps(vessel))