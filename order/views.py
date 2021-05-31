from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Commande, Client, Cartdb, Statut
from cart.forms import CartAddProduitForm, CartUpdateForm
from django.contrib import messages
from datetime import datetime
from django.db import connection
from django.contrib.auth.decorators import login_required


@login_required
def order_list(request, date_before=None, date_after=None, statut_request=None, client_request=None):

    # orders_list = Commande.objects.filter(statut="En cours")

    date_before = request.GET.get('date_before')
    date_after = request.GET.get('date_after')
    client_request = request.GET.get('client_request')
    statut_request = request.GET.get('statut')

    if statut_request and statut_request != "All":
        statut_cmd = get_object_or_404(Statut, id=statut_request)
        orders_list = Commande.objects.filter(statut=statut_cmd).order_by('-date')
    else:
        orders_list = Commande.objects.filter(statut__isnull=False).order_by('-date')
        print(orders_list.query)

    clients = Client.objects.all()
    statuts = Statut.objects.all()

    client_cmd = None
    statut_cmd = None

    if date_after:
        orders_list = orders_list.filter(date__gte=datetime.strptime(date_after, '%Y-%m-%d'))

    if date_before:
        orders_list = orders_list.filter(date__lte=datetime.strptime(date_before, '%Y-%m-%d'))

    if client_request:
        client_cmd = get_object_or_404(Client, id=client_request)
        orders_list = orders_list.filter(client=client_cmd)

    paginator = Paginator(orders_list, 10)
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
               'orders_list': orders_list,
               'date_after': date_after,
               'date_before': date_before,
               'statut_cmd': statut_cmd,
               'statuts': statuts,
               'paginate': True
               }
    return render(request, 'order/list.html', context)


@login_required
def order_detail(request, id):
    # order = Commande.objects.filter(id=id)
    commande = get_object_or_404(Commande, id=id)
    orders = Cartdb.objects.filter(commande=commande)
    context = {
        'commande': commande,
        'orders': orders,
    }

    return render(request, 'order/detail.html', context)


@login_required
def order_valid(request, id):

    context = {
        'toto': 'Coucou',
    }
    return render(request, 'order/valid.html', context)


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
        Commande.objects.filter(pk=commande.id).update(total=total_commande)

        message = "Mise à jour des quantités effectuée avec succès !"
        messages.success(request, message)

    return redirect('order:order_detail', order.commande.id)


@login_required
def order_remove(request, id):
    order = get_object_or_404(Cartdb, id=id)
    Cartdb.objects.filter(pk=id).delete()

    message = "Suppression du produit effectuée avec succès !"
    messages.success(request, message)
    return redirect('order:order_detail', order.commande.id)


@login_required
def order_cancel(request, id):
    order = get_object_or_404(Commande, pk=id)
    statut = Statut.objects.get(nom='Annulée')
    Commande.objects.filter(pk=id).update(statut=statut)

    message = "Commande annulée avec succès !"
    messages.success(request, message)
    return redirect('order:order_detail', id)
