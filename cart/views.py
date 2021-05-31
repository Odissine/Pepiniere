from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.http import require_POST
from .cart import Cart
from .forms import CartAddProduitForm, CartValidForm
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
        message = cart.add(produit=produit, qte=qte, override_qte=cd['override'])

    return JsonResponse({"data": request.session['cart'], "total": len(request.session['cart']), "message": message})


@login_required
def cart_remove(request, produit_id):
    cart = Cart(request)
    produit = get_object_or_404(Produit, id=produit_id)
    cart.remove(produit)
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
    form = CartValidForm(request.POST or None)

    total_commande = 0
    for item in cart:
        total_commande += float(item['prix']) * item['qte']

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data

        statut_en_cours = Statut.objects.get(nom="En cours")
        print(statut_en_cours)

        commande_create = Commande.objects.create(date=datetime.now, client=cd['client'], remise=0, statut=statut_en_cours, total=total_commande)
        commande_create.save()

        for item in cart:
            total_line = float(item['prix']) * item['qte']
            cart_commande = Cartdb.objects.create(produit=item['produit'], prix=item['prix'], qte=item['qte'], commande=commande_create, total_line=total_line)
            cart_commande.save()

        message = "Commande créée avec succès !"
        messages.success(request, message)

        cart.clear()
        commande_creee = True

    # commandes_list = Commande.objects.filter(statut='En cours').order_by('-date')
    # paginator = Paginator(commandes_list, 21)
    # page = request.GET.get('page')
    #
    # try:
    #     commandes = paginator.page(page)
    # except PageNotAnInteger:
    #     # If page is not an integer, deliver first page.
    #     commandes = paginator.page(1)
    # except EmptyPage:
    #     # If page is out of range (e.g. 9999), deliver last page of results.
    #     commandes = paginator.page(paginator.num_pages)
    # context = {
    #     'commande': commande_create.id,
    #     'commande_creee': commande_creee,
    #     'commandes': commandes,
    #     'commandes_list': commandes_list,
    #     'paginate': True,
    # }
    return redirect('order:order_list')


def cart_cancel(request):
    cart = Cart(request)
    cart.clear()

    message = "Le panier a bien été réinitialisé !"
    messages.success(request, message)

    return redirect('produit_list')
