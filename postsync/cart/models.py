from django.db import models
from django.contrib.auth.models import User
from item.models import Item

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    def total_price(self):
        return sum(item.item.price * item.quantity for item in self.cart_items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.item.name} ({self.quantity})"

    def subtotal(self):
        return self.item.price * self.quantity

class Payment(models.Model):
    """Store Stripe payment details."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=10, default='usd')
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} by {self.user.username} - {self.status}"