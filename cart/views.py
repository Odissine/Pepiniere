from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.http import require_POST
from .cart import Cart
from .forms import CartAddProduitForm, CartValidForm, CartUpdateForm
from onlineshop.models import Produit
from order.models import Cartdb, Commande, Client, Statut
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@require_POST
@login_required
def cart_add(request, produit_id):
    cart = Cart(request)

    produit = get_object_or_404(Produit, id=produit_id)
    form = CartAddProduitForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        message = cart.add(produit=produit, qte=cd['qte'], override_qte=cd['override'])

    messages(request, message)
    return redirect('cart:cart_detail')


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
        message, tags = cart.add(produit=produit, qte=qte, override_qte=cd['override'])

    return JsonResponse({"data": request.session['cart'], "total": len(request.session['cart']), "message": message, "tags": tags})


@login_required
def cart_remove(request, produit_id):
    cart = Cart(request)
    produit = get_object_or_404(Produit, id=produit_id)
    cart.remove(produit)
    return redirect('cart:cart_detail')

@login_required
def cart_update(request, produit_id):
    cart = Cart(request)
    form = CartUpdateForm(request.POST or None)

    if form.is_valid():
        cd = form.cleaned_data
        produit = get_object_or_404(Produit, id=produit_id)
        message = cart.update_qte(produit, cd['qte'])
        cart.update_prix(produit, cd['prix'])
        # message = "Quantités/Produits mis(es) à jour avec succès !"
        messages.success(request, message)

    return redirect('cart:cart_detail')


@login_required
def cart_detail(request):
    # user = request.user.is_authenticated
    # if user is False:
    #    return redirect('produit_list')

    cart = Cart(request)
    if len(cart)==0:
        return redirect('produit_list')

    clients = Client.objects.all()

    context = {
        'cart': cart,
        'clients': clients,
    }
    return render(request, 'cart/detail.html', context)


@login_required
def cart_valid(request):
    cart = Cart(request)
    commande_creee = False

    if request.method == "POST":

        total_commande = 0
        for item in cart:
            total_commande += float(item['prix']) * item['qte']

    if len(request.POST['client']) > 0:
        client = Client.objects.get(pk=request.POST['client'])
        statut_en_cours = Statut.objects.get(nom="En cours")
        remise_client = client.remise

        commande_create = Commande.objects.create(date=datetime.now, client=client, remise=remise_client, statut=statut_en_cours, total=total_commande)
        commande_create.save()

        for item in cart:
            total_line = float(item['prix']) * item['qte']
            cart_commande = Cartdb.objects.create(produit=item['produit'], prix=item['prix'], qte=item['qte'], commande=commande_create, total_line=total_line)
            cart_commande.save()
            qte_product_id = Produit.objects.get(nom=item['produit'])
            new_qte = qte_product_id.stock_bis - item['qte']
            Produit.objects.filter(nom=item['produit']).update(stock_bis=new_qte)

        message = "Commande créée avec succès !"
        messages.success(request, message)

        cart.clear()
        commande_creee = True
    else:
        message = "Veuillez selectionner un client pour cette commande !"
        messages.warning(request, message)
        return redirect('cart:cart_detail')

    return redirect('order:order_list')


def cart_cancel(request):
    cart = Cart(request)
    cart.clear()

    message = "Le panier a bien été réinitialisé !"
    messages.success(request, message)

    return redirect('produit_list')
