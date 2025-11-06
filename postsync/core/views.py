from django.shortcuts import render,redirect
from item.models import Category,Item
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm

# Create your views here.

from django.db.models import Count, Q

def index(request):
    items = Item.objects.filter(is_sold=False)[:6]
    categories = Category.objects.annotate(
        unsold_count=Count('items', filter=Q(items__is_sold=False))
    )

    return render(request, 'core/index.html', {
        'categories': categories,
        'items': items
    })


def contact(request):
    return render(request, 'core/contact.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('/login/')
    else:
        form = SignUpForm()

    return render(request, 'core/signup.html', {
        'form': form
    }) 

@login_required
def logout_view(request):
    logout(request)
    return redirect('core:index')