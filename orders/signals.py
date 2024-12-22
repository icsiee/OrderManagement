from django.db.models.signals import post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Customer

@receiver(post_delete, sender=Customer)
def broadcast_customer_deletion(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "orders",
        {
            "type": "send_order_update",
            "data": {"message": f"Müşteri {instance.customer_name} silindi."},
        }
    )
