from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from item.models import Item
from .models import Cart, CartItem

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart_view.html', {'cart': cart})


@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart:view_cart')


@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
    cart_item.delete()
    return redirect('cart:view_cart')
