from django.urls import path
from order_management.consumers import OrderConsumer

websocket_urlpatterns = [
    path("ws/orders/", OrderConsumer.as_asgi()),
]
