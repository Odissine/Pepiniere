from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.db import connection
from django.contrib.auth.decorators import login_required
from django_xhtml2pdf.utils import generate_pdf
from django.http import HttpResponse, JsonResponse, FileResponse

from .models import Commande, Client, Cartdb, Statut, Frais
from onlineshop.models import Produit
from cart.forms import CartAddProduitForm, CartUpdateForm, RemiseUpdateForm

from datetime import datetime
import io
import locale

locale.setlocale(locale.LC_ALL, 'fr_FR')

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
    frais_commandes = Frais.objects.all()
    frais = commande.frais
    total_commande = 0
    for order in orders:
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
        frais_commande = 0
        frais_ht = 0
        tva_frais = 0
        frais_tva = 0

    total_global = total_post_remise + frais_commande

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
    }

    return render(request, 'order/detail.html', context)


@login_required
def order_valid(request, id):
    order = get_object_or_404(Commande, pk=id)
    statut = Statut.objects.get(nom='Validée')
    Commande.objects.filter(pk=id).update(statut=statut, date_update=datetime.now())
    items = Cartdb.objects.filter(commande=order)
    print(order)
    for item in items:

        produit = Produit.objects.get(nom=item.produit)
        print('Ancien Stock : ', produit.stock)
        new_stock = produit.stock - item.qte
        print('Nouveau Stock : ', new_stock)
        # print(item.produit)
        # Produit.objects.filter()
        produit.stock = new_stock
        produit.save()

    message = "Commande validée avec succès :)"
    messages.success(request, message)
    return redirect('order:order_detail', id)


@login_required
def order_update_qte_prix(request, id):
    order = get_object_or_404(Cartdb, id=id)

    if request.method == "POST":

        prix = float(request.POST['prix'].replace(',', '.'))
        print("Prix", type(prix))
        qte = int(request.POST['qte'])
        print("Qte", type(qte))
        if isinstance(prix, float) and isinstance(qte, int):

            item_qte = Cartdb.objects.get(pk=id).qte
            new_total = qte * prix

            # ON MET A JOUR LE PRODUIT DE LA COMMANDE AVEC LA NOUVELLE QUANTITE ET LE NOUVEAU TOTAL
            Cartdb.objects.filter(pk=id).update(qte=qte, prix=prix, total_line=new_total)

            commande = Cartdb.objects.get(pk=id).commande

            # ON RECUPERE TOUS LES PRODUITS DE LA COMMANDE POUR CALCULER LE NOUVEAU TOTAL DE LA COMMANDE
            items = Cartdb.objects.filter(commande=commande)
            total_commande = 0
            for item in items:
                total_commande += item.total_line

            # ON MET A JOUR LA COMMANDE AVEC LE NOUVEAU TOTAL
            Commande.objects.filter(pk=commande.id).update(total=total_commande)

            message = "Mise à jour quantités / prix effectuée avec succès !"
            messages.success(request, message)

        else:
            message = "Erreur dans la saisie du prix unitaire ou de la quantité !"
            messages.error(request, message)

    return redirect('order:order_detail', order.commande.id)


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
def order_update_price(request, id):
    # order = get_object_or_404(Cartdb, id=id)

    if request.method == "POST":

        prix = float(request.POST['prix'])
        if isinstance(prix, float):

            item_qte = Cartdb.objects.get(pk=id).qte
            new_total = item_qte * prix

            # ON MET A JOUR LE PRODUIT DE LA COMMANDE AVEC LA NOUVELLE QUANTITE ET LE NOUVEAU TOTAL
            Cartdb.objects.filter(pk=id).update(prix=prix, total_line=new_total)

            commande = Cartdb.objects.get(pk=id).commande

            # ON RECUPERE TOUS LES PRODUITS DE LA COMMANDE POUR CALCULER LE NOUVEAU TOTAL DE LA COMMANDE
            items = Cartdb.objects.filter(commande=commande)
            total_commande = 0
            for item in items:
                total_commande += item.total_line

            # ON MET A JOUR LA COMMANDE AVEC LE NOUVEAU TOTAL
            Commande.objects.filter(pk=commande.id).update(total=total_commande)

            message = "Mise à jour des quantités effectuée avec succès !"
            messages.success(request, message)

        else:
            message = "Erreur dans la saisie du prix unitaire !"
            messages.error(request, message)

    return redirect('order:order_detail', commande.id)


@login_required
def order_update_remise(request, id):

    remise = locale.atof(request.POST['remise'])

    Commande.objects.filter(pk=id).update(remise=remise)
    commande = Commande.objects.get(pk=id)

    # message = "Mise à jour du taux de remise effectuée avec succès !"
    # messages.success(request, message)

    # return redirect('order:order_detail', order.commande.id)
    return JsonResponse({"remise_taux": remise})

@login_required
def order_update_frais(request, id):
    commande = Commande.objects.get(pk=id)
    frais = int(request.POST.get("frais"))

    #form = CartAddProduitForm(request.POST)
    #
    #if form.is_valid():
    #    cd = form.cleaned_data
    commande.add_frais(frais=frais)

    frais_commande = commande.frais.prix
    frais_ht = frais_commande / (1 + (commande.frais.tva / 100))
    tva_frais = frais_ht * commande.frais.tva / 100

    return JsonResponse({"prix_frais": frais_commande, "tva_frais": commande.frais.tva, "frais_ht": frais_ht, "tva_montant_frais": tva_frais})


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


@login_required
def order_end(request, id):
    order = get_object_or_404(Commande, pk=id)
    statut = Statut.objects.get(nom='Terminée')
    Commande.objects.filter(pk=id).update(statut=statut)

    message = "Commande terminée avec succès !"
    messages.success(request, message)
    return redirect('order:order_detail', id)


def order_print_old(request, id):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')


def order_print(request, id):
    data = {}
    # template = get_template('liste_adresse.html')
    # html = template.render(Context(data))
    # html = open('liste_adresse.pdf', "w+b")
    # pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file, encoding='utf-8')
    model = Commande
    resp = HttpResponse(content_type='application/pdf')
    result = generate_pdf('template_pdf.html', file_object=resp)
    # file.seek(0)
    # pdf = file.read()
    # file.close()
    return result
