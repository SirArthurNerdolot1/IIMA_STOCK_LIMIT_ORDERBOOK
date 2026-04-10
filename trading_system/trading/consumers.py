# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class OrderBookConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        print(f"Client connected: {self.channel_name}")
        await self.channel_layer.group_add('orderbook_group', self.channel_name)
        await self.accept()

    # async def receive(self, text_data):
    #     data = json.loads(text_data)
      
    #     await self.channel_layer.group_send(
    #         self.room_group_name,
    #         {
    #             'type': 'orderbook_update',
    #             'data': data
    #         }
    #     )




    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('orderbook_group', self.channel_name)

    async def send_order_update(self, event):
        print("Sending update to client")
        await self.send(text_data=json.dumps(event['payload']))
