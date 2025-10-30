from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from item.models import Item
import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cart, Payment,CartItem

stripe.api_key = settings.STRIPE_SECRET_KEY

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



@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cart_items.all()

        if not cart_items:
            messages.warning(request, "Your cart is empty.")
            return redirect('cart:view_cart')

        total_amount = sum(item.item.price * item.quantity for item in cart_items)

        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': ci.item.name},
                    'unit_amount': int(ci.item.price * 100),
                },
                'quantity': ci.quantity,
            }
            for ci in cart_items
        ]

        # ✅ Create checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/cart/success/') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri('/cart/cancel/'),
        )

        # ✅ Save Payment record with session.id instead
        Payment.objects.create(
            user=request.user,
            amount=total_amount,
            stripe_session_id=session.id,  # new field (optional)
            status='pending',
        )

        return redirect(session.url, code=303)

    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect('cart:view_cart')

# cart/views.py (continued)
@login_required
def payment_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, "Session not found.")
        return redirect('cart:view_cart')

    session = stripe.checkout.Session.retrieve(session_id)
    payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)

    payment = Payment.objects.filter(stripe_payment_intent=payment_intent.id).first()
    if payment:
        payment.status = 'completed'
        payment.save()

    # Mark items as sold and clear cart
    cart = Cart.objects.get(user=request.user)
    for ci in cart.cart_items.all():
        item = ci.item
        item.is_sold = True
        item.save()
    cart.cart_items.all().delete()

    messages.success(request, "✅ Payment successful! Thank you for your purchase.")
    return render(request, 'cart/payment_success.html', {'payment': payment})


@login_required
def payment_cancel(request):
    messages.warning(request, "❌ Payment cancelled.")
    return render(request, 'cart/payment_cancel.html')
