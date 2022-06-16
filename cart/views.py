from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.http import require_POST
from .cart import Cart
from .forms import CartAddProduitForm, CartValidForm, CartUpdateForm
from onlineshop.models import Produit
from order.models import *
from account.core import *
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.html import format_html
from pepiniere.settings import DEBUG


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
        messages, tags = cart.add(request=request, produit=produit, qte=qte, override_qte=cd['override'])

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
    # form = CartUpdateForm(request.POST or None)
    # if form.is_valid():
    # cd = form.cleaned_data
    produit = get_object_or_404(Produit, id=produit_id)
    try:
        qte = int(request.POST.get('qte'))
    except:
        qte = 0
    message, tags = cart.update_qte(request, produit, qte)
    if request.user.is_staff:
        try:
            prix = float(request.POST.get('prix'))
        except:
            prix = 15
        cart.update_prix(produit, prix)
        # message = "Quantités/Produits mis(es) à jour avec succès !"
    if tags == "success":
        messages.success(request, message)
    else:
        messages.error(request, message)

    return redirect('cart:cart-detail')


@login_required
def cart_detail(request):
    admin = AccessMode.objects.filter(user=request.user).first()
    # user = request.user.is_authenticated
    # if user is False:
    #    return redirect('onlineshop:produit-list')
    if not request.user.is_staff:
        client = Client.objects.get(user=request.user)
        form = CartValidForm(initial={'clients': client})
    else:
        form = CartValidForm(request.POST or None)

    cart = Cart(request)
    if len(cart) == 0:
        return redirect('onlineshop:produit-list')

    clients = Client.objects.all()

    context = {
        'form': form,
        'cart': cart,
        'clients': clients,
        'access_mode': admin,
    }
    return render(request, 'cart/detail.html', context)


@login_required
def cart_valid(request):
    cart = Cart(request)
    form = CartValidForm(request.POST or None)
    mode = request.POST.get('cart-valid-mode')

    if request.method == "POST":
        if form.is_valid():

            if not request.user.is_staff:
                client = Client.objects.get(user=request.user)
            else:
                client = form.cleaned_data['clients']

            if client is not None:
                message = ""
                # COMMANDE NORMALE (STATUT EN COURS)
                if mode == 'normal':
                    inventaire = Inventaire.objects.get(actif=True)
                    for item in cart:
                        produit = Produit.objects.get(nom=item['produit'])
                        new_qte = produit.stock_bis - item['qte']
                        if new_qte < 0:
                            message = format_html("Impossible de créer la commande.<br>Stock insuffisant pour le produit : " + produit.nom)
                            messages.error(request, message)
                            return redirect('cart:cart-detail')

                    # STATUT DE LA COMMANDE EN FONCTION DE QUI EST CONNECTE (STAFF OU USER)
                    if request.user.is_staff:
                        statut_en_cours = Statut.objects.get(nom="En cours")
                        statut = "En cours"
                    else:
                        statut_en_cours = Statut.objects.get(nom="En attente")
                        statut = "En attente"

                    remise_client = client.remise
                    tva = Tva.objects.get(default=True)

                    commande_create = Commande.objects.create(client=client, remise=remise_client, statut=statut_en_cours, tva=tva, inventaire=inventaire)
                    # commande_create.save()

                    for item in cart:
                        cart_commande = Cartdb.objects.create(produit=item['produit'], prix=item['prix'], qte=item['qte'], commande=commande_create)
                        cart_commande.save()
                        if statut == "En cours":
                            produit = Produit.objects.get(nom=item['produit'])
                            new_qte = produit.stock_bis - item['qte']
                            Produit.objects.filter(nom=item['produit']).update(stock_bis=new_qte)

                    config = Config.objects.first()
                    if config.register is True:
                        if DEBUG is True:
                            # href = "http://127.0.0.1:8000/order/detail/" + str(commande_create.id)
                            href = "https://stock.lapetitepepiniere.fr/order/detail/" + str(commande_create.id)
                        else:
                            href = "https://stock.lapetitepepiniere.fr/order/detail/" + str(commande_create.id)

                        # MAIL AU RESPONSABLE
                        email_html = "<br/><br/>Bonjour,<br/><br/>"
                        email_html += "Une nouvelle commande vient d'être passée."
                        email_html += "Client : " + str(client) + "<br/><br/>"
                        email_html += "<a href='" + href + "'>Accéder à la commande</a><br/><br/>"
                        email_html += "La petite pepinière"
                        # send_mail("Nouvelle Commande de " + str(client), email_html, '', '', config_mail['sender'], '')

                        # MAIL AU CLIENT
                        email_html = "<br/><br/>Bonjour " + str(client) + ",<br/><br/>"
                        email_html += "Votre commande a bien été enregistrée.<br/>"
                        email_html += "Elle sera étudiée prochainement et vous serez informé par mail dès lors qu'elle sera validée ou annulée.<br/><br/>"
                        email_html += "<a href='" + href + "'>Accéder à la commande</a><br/><br/>"
                        email_html += "La petite pepinière"
                        # send_mail("La petite pépinère : Commande enregistrée", email_html, '', '', client.mail, '')

                    message = "Commande créée avec succès !"

                # PRE COMMANDE (STATUT PRE-COMMANDE)
                if mode == 'pre':

                    # TODO
                    # ZONE A MODIFIER POUR L'ANNEE PROCHAINE
                    # ###############################################
                    inventaire = Inventaire.objects.get(actif=True)
                    statut_en_cours = Statut.objects.get(nom="Pré-commande")
                    remise_client = client.remise
                    tva = Tva.objects.get(default=True)

                    commande_create = Commande.objects.create(date=datetime.now(), client=client, remise=remise_client, statut=statut_en_cours, tva=tva,
                                                              inventaire=inventaire)
                    commande_create.save()

                    for item in cart:
                        cart_commande = Cartdb.objects.create(produit=item['produit'], prix=item['prix'], qte=item['qte'], commande=commande_create)
                        cart_commande.save()
                        produit = Produit.objects.get(nom=item['produit'])
                        new_qte = produit.stock_future + item['qte']
                        Produit.objects.filter(nom=item['produit']).update(stock_future=new_qte)

                    message = "Pré-commande créée avec succès !"
                messages.success(request, message)
                cart.clear()
        else:
            message = "Veuillez selectionner un client pour valider le panier !"
            messages.error(request, message)
            return redirect('cart:cart-detail')

    return redirect('order:order-list')


def cart_cancel(request):
    cart = Cart(request)
    cart.clear()

    message = "Le panier a bien été réinitialisé !"
    messages.success(request, message)

    return redirect('onlineshop:produit-list')
