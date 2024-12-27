import json
from channels.generic.websocket import AsyncWebsocketConsumer

class StockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("stock_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("stock_updates", self.channel_name)

    async def receive(self, text_data):
        # Gelen mesajı işleme
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Tüm gruba mesaj gönder
        await self.channel_layer.group_send(
            "stock_updates",
            {
                "type": "stock_update",
                "message": message,
            },
        )

    async def stock_update(self, event):
        message = event["message"]

        # İstemciye mesaj gönder
        await self.send(text_data=json.dumps({"message": message}))
