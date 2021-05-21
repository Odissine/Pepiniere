from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .cart import Cart
from .forms import CartAddProduitForm
from onlineshop.models import Produit


@require_POST
def cart_add(request, produit_id):
    cart = Cart(request)
    produit = get_object_or_404(Produit, id=produit_id)
    form = CartAddProduitForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(produit=produit, qte=cd['qte'], override_qte=cd['override'])

    return redirect('cart:cart_detail')


def cart_remove(request, produit_id):
    cart = Cart(request)
    produit = get_object_or_404(Produit, id=produit_id)
    cart.remove(produit)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})


