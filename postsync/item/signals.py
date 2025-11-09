import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Item

MAKE_WEBHOOK_URL = "https://hook.eu2.make.com/o27xsc8nnggo9b6jpjph0f3rni1sl5z6"  # replace with your Make URL

@receiver(post_save, sender=Item)
def send_to_make(sender, instance, created, **kwargs):
    if created:
        data = {
            "name": instance.name,
            "description": instance.description or "",
            "price": instance.price,
            "image_url": instance.image.url if instance.image else "",
        }
        print(f"Data uploaded to Cloudinary")
        try:
            requests.post(MAKE_WEBHOOK_URL, json=data)
            print(f"Sent '{instance.name}' to Make webhook")
        except Exception as e:
            print(f"Failed to send to Make: {e}")