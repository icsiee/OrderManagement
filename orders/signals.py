from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Product

@receiver(post_save, sender=Product)
def notify_product_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    message = {
        "product_id": instance.product_id,
        "product_name": instance.product_name,
        "stock": instance.stock,
        "price": str(instance.price),
    }
    async_to_sync(channel_layer.group_send)(
        "product_updates",
        {"type": "send_product_update", "message": message}
    )
