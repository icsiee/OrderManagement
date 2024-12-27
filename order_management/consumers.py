# orders/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'order_updates'  # Odayı belirleyin
        self.room_group_name = f'order_{self.room_name}'

        # WebSocket bağlantısını kabul et
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # WebSocket bağlantısı kurulduğunda yanıt gönder
        await self.accept()

    async def disconnect(self, close_code):
        # Bağlantı kapanırken grubundan çıkar
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Grup mesajı alındığında çalışacak
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        order_status = text_data_json['status']

        # Mesajı gruptaki tüm kullanıcılara gönder
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'order_status_update',
                'status': order_status
            }
        )

    # Grup mesajı alındığında çalışacak
    async def order_status_update(self, event):
        status = event['status']

        # WebSocket'e gönderilecek mesaj
        await self.send(text_data=json.dumps({
            'status': status
        }))
