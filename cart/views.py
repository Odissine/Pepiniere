from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.http import require_POST
from .cart import Cart
from .forms import CartAddProduitForm, CartValidForm
from onlineshop.models import Produit
from order.models import Cartdb, Commande, Client
from account.decorators import unauthenticated_user
from datetime import datetime


@require_POST
#@unauthenticated_user
def cart_add(request, produit_id):
    cart = Cart(request)
    produit = get_object_or_404(Produit, id=produit_id)
    form = CartAddProduitForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(produit=produit, qte=cd['qte'], override_qte=cd['override'])

    return redirect('cart:cart_detail')

#@unauhenticated_user
def cart_remove(request, produit_id):
    cart = Cart(request)
    produit = get_object_or_404(Produit, id=produit_id)
    cart.remove(produit)
    return redirect('cart:cart_detail')

#@unauthenticated_user
def cart_detail(request):
    cart = Cart(request)
    clients = Client.objects.all()

    context = {
        'cart': cart,
        'clients': clients,
    }
    return render(request, 'cart/detail.html', context)


def cart_valid(request):
    cart = Cart(request)
    commande_creee = False
    form = CartValidForm(request.POST or None)

    total_commande = 0
    for item in cart:
        total_commande += float(item['prix']) * item['qte']

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        commande_create = Commande.objects.create(date=datetime.now, client=cd['client'], remise=0, statut='En cours', total=total_commande)
        commande_create.save()

        for item in cart:
            total_line = float(item['prix']) * item['qte']
            cart_commande = Cartdb.objects.create(produit=item['produit'], prix=item['prix'], qte=item['qte'], commande=commande_create, total_line=total_line)
            cart_commande.save()

        cart.clear()
        commande_creee = True
    commandes_list = Commande.objects.filter(statut='En cours').order_by('-date')
    paginator = Paginator(commandes_list, 21)
    page = request.GET.get('page')

    try:
        commandes = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        commandes = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        commandes = paginator.page(paginator.num_pages)
    context = {
        'commande': commande_create.id,
        'commande_creee': commande_creee,
        'commandes': commandes,
        'commandes_list': commandes_list,
        'paginate': True,
    }
    return redirect('order:order_list')
