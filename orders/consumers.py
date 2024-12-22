from channels.generic.websocket import AsyncWebsocketConsumer

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "orders"
        # Kanalı gruba ekle
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Kanalı gruptan çıkar
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Gelen mesajları işle
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": text_data,
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=message)
