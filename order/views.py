from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.db import connection
from django.contrib.auth.decorators import login_required
from django_xhtml2pdf.utils import generate_pdf
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.generic import View
from django.template.loader import get_template
from django.conf import settings
from .utils import render_to_pdf
from .models import Commande, Client, Cartdb, Statut, Frais
from onlineshop.models import Produit, Variete
from cart.forms import CartAddProduitForm, CartUpdateForm, RemiseUpdateForm
from .forms import OrderAddProduitOrder

from datetime import datetime, date
import io
import locale

locale.setlocale(locale.LC_ALL, 'C')


@login_required
def order_list(request, date_before=None, date_after=None, statut_request=None, client_request=None):
    # orders_list = Commande.objects.filter(statut="En cours")

    # Récupération des valeurs issues du formulaire
    date_before = request.POST.get('date_before')
    date_after = request.POST.get('date_after')
    client_request = request.POST.get('client_request')
    statut_request = request.POST.get('statut')
    variete_request = request.POST.get('variete')

    # RECUPERATION DES VARIETES DES COMMANDES PASSEES ______________________________________________
    varietes_list = []
    all_orders = Commande.objects.all()
    for all_order in all_orders:
        items = Cartdb.objects.filter(commande=all_order)
        for item in items:
            if item.produit.variete not in varietes_list:
                varietes_list.append(item.produit.variete)
    varietes_list = sorted(varietes_list, key=lambda x: x.nom)

    # REQUETE SUR COMMANDE EN FONCTION DU STATUT ____________________________________________________
    if statut_request and statut_request != "All":
        statut_cmd = get_object_or_404(Statut, id=statut_request)
        orders_obj = Commande.objects.filter(statut=statut_cmd).order_by('-date')
        statut_request = int(statut_request)
    else:
        orders_obj = Commande.objects.filter(statut__isnull=False).order_by('-date')

    clients = Client.objects.all()
    statuts = Statut.objects.all()

    client_cmd = None
    statut_cmd = None

    # REQUETE SUR COMMANDE EN FONCTION DE LA VARIETE ________________________________________________
    commandes_list = []

    if variete_request  and variete_request != "All":
        # Recuperation de l'objet Variete
        variete_order = get_object_or_404(Variete, pk=variete_request)

        # Recuperation des produits associés à cette variété
        produits_variete = Produit.objects.filter(variete=variete_order)

        for produit_variete in produits_variete:
            orders_varietes = Cartdb.objects.filter(produit=produit_variete)
            for order_variete in orders_varietes:
                commandes_list.append(order_variete.commande)

    # REQUETE SUR COMMANDE APRES LA DATE
    if date_after:
        orders_obj = orders_obj.filter(date__gte=datetime.strptime(date_after, '%Y-%m-%d'))

    # REQUETE SUR COMMANDE AVANT LA DATE
    if date_before:
        orders_obj = orders_obj.filter(date__lte=datetime.strptime(date_before, '%Y-%m-%d'))

    # REQUETE SUR COMMANDE D'UN CLIENT
    if client_request:
        client_cmd = get_object_or_404(Client, id=client_request)
        orders_obj = orders_obj.filter(client=client_cmd)

    orders_list = []
    for x in orders_obj:
        orders_list.append(x)

    if len(commandes_list)>0:
        nouveau = set(orders_list).intersection(commandes_list)
        # Créer la nouvelle liste en utilisant la concaténation de liste
        orders_list_objects = list(nouveau)
    else:
        orders_list_objects = orders_list

    paginator = Paginator(orders_list_objects, 20)
    page = request.GET.get('page')

    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        orders = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        orders = paginator.page(paginator.num_pages)

    context = {'client_cmd': client_cmd,
               'clients': clients,
               'orders': orders,
               'orders_list': orders_list_objects,
               'date_after': date_after,
               'date_before': date_before,
               'statut_cmd': statut_cmd,
               'statut_request': statut_request,
               'statuts': statuts,
               'varietes_list': varietes_list,
               'variete_request': variete_request,
               'paginate': True
               }
    # print(statut_request)
    # print(type(statut_request))
    return render(request, 'order/list.html', context)


@login_required
def order_detail(request, id):
    # order = Commande.objects.filter(id=id)
    commande = get_object_or_404(Commande, id=id)
    orders = Cartdb.objects.filter(commande=commande)
    frais_commandes = Frais.objects.all().order_by('prix')
    frais = commande.frais
    total_commande = 0
    qte_commande = 0
    for order in orders:
        qte_commande += order.qte
        total_commande += order.total_line

    remise_montant = total_commande * commande.remise / 100
    total_post_remise = total_commande - remise_montant
    total_ht_post_remise = total_post_remise / (1 + (commande.tva / 100))
    tva_post_remise = total_ht_post_remise * commande.tva / 100

    if frais is not None:
        frais_tva = frais.tva
        frais_commande = frais.prix
        frais_ht = frais_commande / (1 + (frais_tva / 100))
        tva_frais = frais_ht * frais_tva / 100

    else:
        frais = Frais.objects.get(nom="Aucun frais")
        frais_commande = 0
        frais_ht = 0
        tva_frais = 0
        frais_tva = 0

    total_global = total_post_remise + frais_commande
    total_global_tva = tva_frais + tva_post_remise
    total_global_ht = frais_ht + total_ht_post_remise

    context = {
        'commande': commande,
        'orders': orders,
        'remise_montant': remise_montant,
        'total_post_remise': total_post_remise,
        'total_ht_post_remise': total_ht_post_remise,
        'tva_post_remise': tva_post_remise,
        'frais_commande': frais_commande,
        'frais_ht': frais_ht,
        'tva_frais': tva_frais,
        'frais_tva': frais_tva,
        'frais_commandes': frais_commandes,
        'frais_id': frais,
        'total_global': total_global,
        'total_global_tva': total_global_tva,
        'total_global_ht': total_global_ht,
        'order_qte': qte_commande,
    }

    return render(request, 'order/detail.html', context)


@login_required
def order_valid(request, id):
    order = get_object_or_404(Commande, pk=id)
    statut = Statut.objects.get(nom='Validée')
    Commande.objects.filter(pk=id).update(statut=statut, date_update=datetime.now())
    items = Cartdb.objects.filter(commande=order)

    message = "Commande validée avec succès :)"
    messages.success(request, message)

    return redirect('order:order_detail', id)


@login_required
def order_update_qte_prix(request, id):
    order = get_object_or_404(Cartdb, id=id)

    if request.method == "POST":

        prix = float(request.POST['prix'].replace(',', '.'))
        qte = int(request.POST['qte'])
        old_qte = int(request.POST['qte_old'])
        if isinstance(prix, float) and isinstance(qte, int):

            item_qte = Cartdb.objects.get(pk=id).qte
            new_total = qte * prix

            # ON MET A JOUR LE PRODUIT DE LA COMMANDE AVEC LA NOUVELLE QUANTITE ET LE NOUVEAU TOTAL
            Cartdb.objects.filter(pk=id).update(qte=qte, prix=prix, total_line=new_total)

            # ON MET A JOUR LES QTE VIRTUELLES DU PRODUIT
            produit = Cartdb.objects.get(pk=id).produit
            produit = Produit.objects.get(nom=produit)
            new_stock = produit.stock_bis - (qte - old_qte)
            produit.stock_bis = new_stock
            produit.save()

            commande = Cartdb.objects.get(pk=id).commande
            # ON RECUPERE TOUS LES PRODUITS DE LA COMMANDE POUR CALCULER LE NOUVEAU TOTAL DE LA COMMANDE
            items = Cartdb.objects.filter(commande=commande)
            total_commande = 0
            for item in items:
                total_commande += item.total_line

            # ON MET A JOUR LA COMMANDE AVEC LE NOUVEAU TOTAL
            Commande.objects.filter(pk=commande.id).update(total=total_commande, date_update=datetime.now())

            message = "Mise à jour quantités / prix effectuée avec succès !"
            messages.success(request, message)

        else:
            message = "Erreur dans la saisie du prix unitaire ou de la quantité !"
            messages.warning(request, message)

    return redirect('order:order_detail', order.commande.id)


# MISE A JOUR DES QTE SUR UN ITEM DE LA COMMANDE
@login_required
def order_update(request, id):
    order = get_object_or_404(Cartdb, id=id)
    form = CartUpdateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data

        item_prix = Cartdb.objects.get(pk=id).prix
        new_total = item_prix * cd['qte']

        commande = Cartdb.objects.get(pk=id).commande

        # ON MET A JOUR LE PRODUIT DE LA COMMANDE AVEC LA NOUVELLE QUANTITE ET LE NOUVEAU TOTAL
        Cartdb.objects.filter(pk=id).update(qte=cd['qte'], total_line=new_total)

        # ON RECUPERE TOUS LES PRODUITS DE LA COMMANDE POUR CALCULER LE NOUVEAU TOTAL DE LA COMMANDE
        items = Cartdb.objects.filter(commande=commande)
        total_commande = 0
        for item in items:
            total_commande += item.total_line

        # ON MET A JOUR LA COMMANDE AVEC LE NOUVEAU TOTAL
        Commande.objects.filter(pk=commande.id).update(total=total_commande, date_update=datetime.now())

        message = "Mise à jour des quantités effectuée avec succès !"
        messages.success(request, message)

    return redirect('order:order_detail', order.commande.id)


# MISE A JOUR DES PRIX SUR UN ITEM DE LA COMMANDE
@login_required
def order_update_price(request, id):
    # order = get_object_or_404(Cartdb, id=id)

    if request.method == "POST":

        prix = float(request.POST['prix'])
        if isinstance(prix, float):

            item_qte = Cartdb.objects.get(pk=id).qte
            new_total = item_qte * prix

            # ON MET A JOUR LE PRODUIT DE LA COMMANDE AVEC LE NOUVEAU PRIX ET LE NOUVEAU TOTAL
            Cartdb.objects.filter(pk=id).update(prix=prix, total_line=new_total)

            commande = Cartdb.objects.get(pk=id).commande

            # ON RECUPERE TOUS LES PRODUITS DE LA COMMANDE POUR CALCULER LE NOUVEAU TOTAL DE LA COMMANDE
            items = Cartdb.objects.filter(commande=commande)
            total_commande = 0
            for item in items:
                total_commande += item.total_line

            # ON MET A JOUR LA COMMANDE AVEC LE NOUVEAU TOTAL
            Commande.objects.filter(pk=commande.id).update(total=total_commande, date_update=datetime.now())

            message = "Mise à jour des prix unitaires effectuée avec succès !"
            messages.success(request, message)

        else:
            message = "Erreur dans la saisie du prix unitaire !"
            messages.warning(request, message)

    return redirect('order:order_detail', commande.id)


# MISE A JOUR DE LA REMISE SUR UNE COMMANDE (AJAX - CHANGE INPUT)
@login_required
def order_update_remise(request, id):
    remise = locale.atof(request.POST['remise'])

    Commande.objects.filter(pk=id).update(remise=remise)
    commande = Commande.objects.get(pk=id)

    message = "Remise modifiée avec succès !"
    messages.success(request, message)

    # return redirect('order:order_detail', order.commande.id)
    return JsonResponse({"remise_taux": remise})


# MISE A JOUR DES FRAIS SUR UNE COMMANDE (AJAX - CHANGE INPUT)
@login_required
def order_update_frais(request, id):
    commande = Commande.objects.get(pk=id)

    if (request.POST.get("frais")) == "" or (request.POST.get("frais")) == 1:
        frais_commande = ""
        frais_ht = ""
        tva_frais = ""
        tva_montant_frais = ""
        commande.add_frais(frais=None)
    else:
        frais = int(request.POST.get("frais"))
        commande.add_frais(frais=frais)
        frais_commande = commande.frais.prix
        frais_ht = frais_commande / (1 + (commande.frais.tva / 100))
        tva_montant_frais = frais_ht * commande.frais.tva / 100
        tva_frais = commande.frais.tva
    remise = commande.remise
    total = commande.total
    total_post_remise = total - (total * remise / 100)
    total_ht_post_remise = total_post_remise / (1 + (commande.tva / 100))
    tva_commande = total_ht_post_remise * commande.tva / 100

    message = "Frais modifié avec succès !"
    messages.success(request, message)

    return JsonResponse({"prix_frais": frais_commande, "tva_frais": tva_frais, "frais_ht": frais_ht,
                         "tva_montant_frais": tva_montant_frais,
                         "tva_montant_global": tva_commande})


# AJOUT D'UN PRODUIT SUR UNE COMMANDE
@login_required
def order_update_add_product(request):
    if (request.POST.get("recipient-order")) != "" and (request.POST.get("produit-id")) != "":
        order_id = request.POST.get("recipient-order")
        produit_id = request.POST.get("produit-id")
        order = get_object_or_404(Commande, pk=order_id)
        produit = get_object_or_404(Produit, pk=produit_id)
        items = Cartdb.objects.filter(commande=order)
        list_produits = []
        for item in items:
            print(item.produit)
            list_produits.append(item.produit)

        if produit in list_produits:
            cart_commande = Cartdb.objects.create(produit=produit, prix=15.0, qte=1, commande=order, total_line=15.0)
            cart_commande.save()

            total = float(order.total) + 15.0
            Commande.objects.filter(pk=order_id).update(total=total)

            stock = produit.stock_bis - 1
            # print(stock)
            Produit.objects.filter(pk=produit_id).update(stock_bis=stock)

            message = "Ajout du produit effectué avec succès !"
            messages.success(request, message)
        else:
            message = "Produit déjà présent dans la commande."
            messages.warning(request, message)
        return redirect('order:order_detail', order.id)
    else:
        return False


# SUPPRESSION D'UN ITEM DE LA COMMANDE
@login_required
def order_remove(request, id):
    order = get_object_or_404(Cartdb, id=id)
    item = Cartdb.objects.get(id=id)
    print("Quantité :", item.qte)
    produit = Cartdb.objects.get(pk=id).produit
    print("Produit concerné : ", produit)
    stock = produit.stock_bis + item.qte
    commande = get_object_or_404(Commande, pk=order.commande.id)
    total = commande.total - item.total_line
    Commande.objects.filter(pk=order.commande.id).update(total=total)
    print("Nouveau stock à mettre à jour : ", stock)
    Produit.objects.filter(pk=produit.id).update(stock_bis=stock)
    Cartdb.objects.filter(pk=id).delete()

    message = "Suppression du produit effectuée avec succès !"
    messages.success(request, message)

    return redirect('order:order_detail', order.commande.id)


# ANNULATION D'UNE COMMANDE AVEC MISE A JOUR DE LA DATE ET DU STATUT
@login_required
def order_cancel(request, id):
    order = get_object_or_404(Commande, pk=id)
    statut = Statut.objects.get(nom='Annulée')
    Commande.objects.filter(pk=id).update(statut=statut)
    Commande.objects.filter(pk=id).update(date_update=datetime.now())

    orders = Cartdb.objects.filter(commande=order)
    for order in orders:
        qte_product_id = Produit.objects.get(nom=order.produit)
        old_qte = qte_product_id.stock_bis + order.qte
        Produit.objects.filter(nom=order.produit).update(stock_bis=old_qte)

    message = "Commande annulée avec succès !"
    messages.success(request, message)
    return redirect('order:order_detail', id)


# COMMANDE TERMINEE AVEC MISE A JOUR DE LA DATE ET DU STATUT
@login_required
def order_end(request, id):
    order = get_object_or_404(Commande, pk=id)
    statut = Statut.objects.get(nom='Terminée')

    Commande.objects.filter(pk=id).update(statut=statut, date_update=datetime.now())
    orders = Cartdb.objects.filter(commande=order)
    for order in orders:
        qte_product_id = Produit.objects.get(nom=order.produit)
        new_qte = qte_product_id.stock - order.qte
        Produit.objects.filter(nom=order.produit).update(stock=new_qte)

    message = "Commande terminée avec succès !"
    messages.success(request, message)
    return redirect('order:order_detail', id)


@login_required
def order_print(request, id, *args, **kwargs):
    try:
        mode = request.GET['mode']
    except:
        mode = "0"

    if mode == "1":
        path_pdf = 'pdf/facture.html'
        type_pdf = "Facture"
    else:
        path_pdf = 'pdf/boncommande.html'
        type_pdf = "Commande"

    template = get_template(path_pdf)
    commande = get_object_or_404(Commande, id=id)
    orders = Cartdb.objects.filter(commande=commande)
    frais_commandes = Frais.objects.all()
    frais = commande.frais
    total_commande = 0
    total_qte = 0

    for order in orders:
        total_commande += order.total_line
        total_qte += order.qte

    remise_montant = total_commande * commande.remise / 100
    total_post_remise = total_commande - remise_montant
    total_ht_post_remise = total_post_remise / (1 + (commande.tva / 100))
    tva_post_remise = total_ht_post_remise * commande.tva / 100

    if frais is not None:
        frais_tva = frais.tva
        frais_commande = frais.prix
        frais_ht = frais_commande / (1 + (frais_tva / 100))
        tva_frais = frais_ht * frais_tva / 100

    else:
        frais = Frais.objects.get(nom="Aucun frais")
        frais_commande = 0
        frais_ht = 0
        tva_frais = 0
        frais_tva = 0

    total_global = total_post_remise + frais_commande
    total_global_tva = tva_frais + tva_post_remise
    total_global_ht = frais_ht + total_ht_post_remise

    image = settings.STATIC_ROOT + '/img/logo_facture.png'

    context = {
        'commande': commande,
        'orders': orders,
        'remise_montant': remise_montant,
        'total_post_remise': total_post_remise,
        'total_ht_post_remise': total_ht_post_remise,
        'tva_post_remise': tva_post_remise,
        'frais_commande': frais_commande,
        'frais_ht': frais_ht,
        'tva_frais': tva_frais,
        'frais_tva': frais_tva,
        'frais_commandes': frais_commandes,
        'frais_id': frais,
        'total_global': total_global,
        'total_global_tva': total_global_tva,
        'total_global_ht': total_global_ht,
        'image': image,
        'order_qte': total_qte,
    }
    html = template.render(context)
    pdf = render_to_pdf(path_pdf, context)

    if pdf:
        # response = HttpResponse(pdf, content_type='application/pdf')
        response = HttpResponse(content_type='application/pdf')
        result = generate_pdf(path_pdf, file_object=response, context=context)

        # response = HttpResponse(html, content_type='text/html')
        filename = type_pdf + "_%s_%s.pdf" % (commande.id, commande.date.strftime('%Y'))
        content = "inline; filename=%s" % filename
        download = request.GET.get("download")
        # download = False
        if download:
            content = "attachment; filename=%s" % filename
        response['Content-Disposition'] = content
        # return response
        return result
    return HttpResponse("Not found")
    # return HttpResponse(pdf, content_type='application/pdf')
    # return HttpResponse(html)


# Modal Search for Client by Name/Firstname for Add in Order
def order_search_client(request):
    nom = request.POST.get("recipient-nom")
    prenom = request.POST.get("recipient-prenom")

    clients = Client.objects.all().values()

    if nom == "" and prenom == "":
        clients = Client.objects.all().values()
    if nom == "":
        clients = Client.objects.filter(prenom__icontains=prenom).values()
    if prenom == "":
        clients = Client.objects.filter(nom__icontains=nom).values()

    return JsonResponse({"clients_json": list(clients)})


# Modal Search for Commande by ID for Add Product in
def order_search_order(request):
    order_id = request.POST.get("recipient-order")
    orders = Commande.objects.all().values()

    if order_id != "":
        orders = Commande.objects.filter(pk=order_id)
    # print(orders)

    return JsonResponse({"orders_json": orders})


@login_required
def order_etiquettes(request):
    date_before = request.POST.get('date_before')
    date_after = request.POST.get('date_after')
    client_request = request.POST.get('client_request')
    statut_request = request.POST.get('statut')
    variete_request = request.POST.get('variete')

    # RECUPERATION DES VARIETES DES COMMANDES PASSEES ______________________________________________
    varietes_list = []
    all_orders = Commande.objects.all()
    for all_order in all_orders:
        items = Cartdb.objects.filter(commande=all_order)
        for item in items:
            if item.produit.variete not in varietes_list:
                varietes_list.append(item.produit.variete)
    varietes_list = sorted(varietes_list, key=lambda x: x.nom)

    if statut_request and statut_request != "All":
        statut_cmd = get_object_or_404(Statut, id=statut_request)
        orders_obj = Commande.objects.filter(statut=statut_cmd).order_by('-date')
        statut_request = int(statut_request)
    else:
        orders_obj = Commande.objects.filter(statut__isnull=False).order_by('-date')

    clients = Client.objects.all()
    statuts = Statut.objects.all()

    client_cmd = None
    statut_cmd = None

    # REQUETE SUR COMMANDE EN FONCTION DE LA VARIETE ________________________________________________
    commandes_list = []

    if variete_request and variete_request != "All":
        # Recuperation de l'objet Variete
        variete_order = get_object_or_404(Variete, pk=variete_request)

        # Recuperation des produits associés à cette variété
        produits_variete = Produit.objects.filter(variete=variete_order)

        for produit_variete in produits_variete:
            orders_varietes = Cartdb.objects.filter(produit=produit_variete)
            for order_variete in orders_varietes:
                commandes_list.append(order_variete.commande)

    if date_after:
        orders_obj = orders_obj.filter(date__gte=datetime.strptime(date_after, '%Y-%m-%d'))

    if date_before:
        orders_obj = orders_obj.filter(date__lte=datetime.strptime(date_before, '%Y-%m-%d'))

    if client_request:
        client_cmd = get_object_or_404(Client, id=client_request)
        orders_obj = orders_obj.filter(client=client_cmd)

    orders_list = []
    for x in orders_obj:
        orders_list.append(x)

    if len(commandes_list) > 0:
        nouveau = set(orders_list).intersection(commandes_list)
        # Créer la nouvelle liste en utilisant la concaténation de liste
        orders_list_objects = list(nouveau)
    else:
        orders_list_objects = orders_list

    context = {'client_cmd': client_cmd,
               'clients': clients,
               'orders_list': orders_list_objects,
               'date_after': date_after,
               'date_before': date_before,
               'statut_cmd': statut_cmd,
               'statut_request': statut_request,
               'statuts': statuts,
               'variete_request': variete_request,
               'varietes_list': varietes_list,
               'paginate': True
               }
    return render(request, 'order/etiquettes.html', context)


def print_etiquettes(request):
    if request.method == "POST":
        query_order_list = request.POST.getlist('checkorder')
        # for order in request.POST.getlist('checkorder'):
        #     print(order)

    commandes = Commande.objects.filter(pk__in=query_order_list)
    orders = Cartdb.objects.filter(commande__in=commandes)
    context = {
        'commandes': commandes,
        'orders': orders,
    }

    path_pdf = 'pdf/etiquettes.html'
    template = get_template(path_pdf)
    html = template.render(context)
    pdf = render_to_pdf(path_pdf, context)

    if pdf:
        # response = HttpResponse(pdf, content_type='application/pdf')
        response = HttpResponse(content_type='application/pdf')
        result = generate_pdf(path_pdf, file_object=response, context=context)

        # response = HttpResponse(html, content_type='text/html')
        today = date.today()
        filename = "Etiquettes_%s.pdf" % (today.strftime('%D%M%Y'))
        content = "inline; filename=%s" % filename
        download = request.POST["download"]
        download = False
        if download:
            content = "attachment; filename=%s" % filename
        response['Content-Disposition'] = content
        # return response
        return result

    return HttpResponse("Not found")
