from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.http import require_POST
from .cart import Cart
from .forms import CartAddProduitForm, CartValidForm, CartUpdateForm
from onlineshop.models import Produit
from order.models import *
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.html import format_html


@require_POST
@login_required
def cart_add(request, produit_id):
    cart = Cart(request)

    produit = get_object_or_404(Produit, id=produit_id)
    qte = int(request.POST.get("qte"))

    form = CartAddProduitForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        message = cart.add(produit=produit, qte=qte, override_qte=cd['override'])
    else:
        message = "Une erreur s'est produite !"

    messages.success(request, message)
    return redirect('cart:cart-detail')


@require_POST
@login_required
def cart_add_ajax(request, produit_id):
    cart = Cart(request)
    produit = get_object_or_404(Produit, id=produit_id)
    qte = int(request.POST.get("qte"))

    form = CartAddProduitForm(request.POST)
    #
    if form.is_valid():
        cd = form.cleaned_data
        messages, tags = cart.add(produit=produit, qte=qte, override_qte=cd['override'])

    return JsonResponse({"data": request.session['cart'], "total": len(request.session['cart']), "messages": messages, "tags": tags})


@login_required
def cart_remove(request, produit_id):
    cart = Cart(request)
    produit = get_object_or_404(Produit, id=produit_id)
    cart.remove(produit)
    return redirect('cart:cart-detail')

@login_required
def cart_update(request, produit_id):
    cart = Cart(request)
    form = CartUpdateForm(request.POST or None)

    if form.is_valid():
        cd = form.cleaned_data
        produit = get_object_or_404(Produit, id=produit_id)
        message, tags = cart.update_qte(produit, cd['qte'])
        cart.update_prix(produit, cd['prix'])
        # message = "Quantités/Produits mis(es) à jour avec succès !"
        if tags == "success":
            messages.success(request, message)
        else:
            messages.error(request, message)

    return redirect('cart:cart-detail')


@login_required
def cart_detail(request):
    # user = request.user.is_authenticated
    # if user is False:
    #    return redirect('onlineshop:produit-list')

    cart = Cart(request)
    if len(cart) == 0:
        return redirect('onlineshop:produit-list')

    clients = Client.objects.all()

    context = {
        'cart': cart,
        'clients': clients,
    }
    return render(request, 'cart/detail.html', context)


@login_required
def cart_valid(request):
    cart = Cart(request)

    if request.method == "POST":
        if len(request.POST['client']) > 0:
            for item in cart:
                produit = Produit.objects.get(nom=item['produit'])
                new_qte = produit.stock_bis - item['qte']
                if new_qte < 0:
                    message = format_html("Impossible de créer la commande.<br>Stock insuffisant pour le produit : " + produit.nom)
                    messages.error(request, message)
                    return redirect('cart:cart-detail')

            client = Client.objects.get(pk=request.POST['client'])
            statut_en_cours = Statut.objects.get(nom="En cours")
            remise_client = client.remise
            tva = Tva.objects.get(default=True)

            commande_create = Commande.objects.create(date=datetime.now, client=client, remise=remise_client, statut=statut_en_cours, tva=tva)
            commande_create.save()

            for item in cart:
                cart_commande = Cartdb.objects.create(produit=item['produit'], prix=item['prix'], qte=item['qte'], commande=commande_create)
                cart_commande.save()
                produit = Produit.objects.get(nom=item['produit'])
                new_qte = produit.stock_bis - item['qte']
                Produit.objects.filter(nom=item['produit']).update(stock_bis=new_qte)

            message = "Commande créée avec succès !"
            messages.success(request, message)

            cart.clear()
        else:
            message = "Veuillez selectionner un client pour valider le panier !"
            messages.error(request, message)
            return redirect('cart:cart-detail')

    return redirect('order:order-list')


@login_required
def pre_cart_valid(request):
    cart = Cart(request)

    if request.method == "POST":
        if len(request.POST['pre_client']) > 0:

            client = Client.objects.get(pk=request.POST['pre_client'])
            statut_pre_commande = Statut.objects.get(nom="Pré-commande")
            tva = Tva.objects.get(default=True)
            commande_create = Commande.objects.create(date=datetime.now(), client=client, remise=client.remise, statut=statut_pre_commande, tva=tva)

            for item in cart:
                produit = Produit.objects.get(nom=item['produit'])
                new_qte = produit.stock_future + item['qte']
                Produit.objects.filter(nom=item['produit']).update(stock_future=new_qte)

                cart_commande = Cartdb.objects.create(produit=item['produit'], prix=item['prix'], qte=item['qte'], commande=commande_create)

            message = "Pré-commande créée avec succès !"
            messages.success(request, message)
            cart.clear()
        else:
            message = "Veuillez selectionner un client pour valider le panier en pré-commande!"
            messages.error(request, message)
            return redirect('cart:cart-detail')

    return redirect('order:order-list')


def cart_cancel(request):
    cart = Cart(request)
    cart.clear()

    message = "Le panier a bien été réinitialisé !"
    messages.success(request, message)

    return redirect('onlineshop:produit-list')
