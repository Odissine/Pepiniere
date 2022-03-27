from datetime import datetime
from sqlite3 import DatabaseError

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.utils.html import format_html
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum
from django.utils.text import slugify
from django.http import JsonResponse
from django.forms import formset_factory

from account.decorators import unauthenticated_user
from account.decorators import allowed_users

from onlineshop.models import *
from onlineshop.forms import *
from onlineshop.core import *
from cart.forms import CartAddProduitForm
from pepiniere import settings
from order.models import *
from .forms import *
from order.forms import *
import xlsxwriter
import io
import json

from openpyxl import load_workbook


@login_required
@staff_member_required
def full_admin(request):
    if request.user.is_authenticated:
        admin = AccessMode.objects.filter(user=request.user).first()
        if admin:
            if admin.admin is True:
                admin.admin = False
            else:
                admin.admin = True
            admin.save()
        else:
            AccessMode.objects.create(user=request.user, admin=True)

    return redirect('produit-list')


def create_tab_dict(items, menu):
    itemslist = []
    for item in items:
        if menu == "variete":
            if item.get_variete() not in itemslist:
                itemslist.append(item.get_variete())
        if menu == "portegreffe":
            if item.get_portegreffe() not in itemslist:
                itemslist.append(item.get_portegreffe())
        if menu == "spec":
            if item.get_spec() not in itemslist:
                itemslist.append(item.get_spec())
    return itemslist


def produit_list(request):
    espece = None
    variete = None
    portegreffe = None
    spec = None
    stock = True
    gaf = False

    formAction = 'onlineshop:produit-list'

    form = SearchProduitForm(request.GET or None)

    if 'p' in request.GET:
        order_value = request.GET['p']
        if order_value == 'total':
            queryset = Produit.objects.annotate(sum=Sum('Cartdbs__qte')).order_by('-sum')
        else:
            queryset = Produit.objects.all().order_by(order_value)
        request.session['p'] = request.GET['p']
    elif 'p' in request.session:
        order_value = request.session['p']
        if order_value == 'total':
            queryset = Produit.objects.annotate(sum=Sum('Cartdbs__qte')).order_by('-sum')
        else:
            queryset = Produit.objects.all().order_by(order_value)
    else:
        queryset = Produit.objects.all().order_by('variete', 'espece', 'portegreffe')

    if request.method == 'GET':
        if form.is_valid():
            espece = form.cleaned_data['especes']
            variete = form.cleaned_data['varietes']
            portegreffe = form.cleaned_data['portegreffes']
            spec = form.cleaned_data['specs']
            stock = form.cleaned_data['stock']
            gaf = form.cleaned_data['gaf']

            if not espece is None:
                queryset = queryset.filter(espece=espece)
            if not variete is None:
                queryset = queryset.filter(variete=variete)
            if not portegreffe is None:
                queryset = queryset.filter(portegreffe=portegreffe)
            if not spec is None:
                queryset = queryset.filter(spec=spec)
            if stock is True:
                queryset = queryset.filter(stock_bis__gt=0)
            if gaf is True:
                queryset = queryset.filter(gaf=True)

    if request.user.is_staff is False:
        stock = True
        gaf = False
        admin_mode = False
        queryset = queryset.filter(gaf=False, stock_bis__gt=0)
    else:
        try:
            admin_mode = AccessMode.objects.get(user=request.user).admin
        except:
            admin_mode = False

    paginator = Paginator(queryset, 50)
    get_data = request.GET.copy()
    page = get_data.pop('page', None)
    p = get_data.pop('p', None)
    if 'page' in request.GET:
        page = request.GET['page']
        request.session['page_p'] = page
    elif 'page_p' in request.session:
        page = request.session['page_p']

    try:
        produits = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        produits = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        produits = paginator.page(paginator.num_pages)

    context = {'produits': produits,
               'produits_list': queryset,
               'paginate': True,
               'form': form,
               'formAction': formAction,
               'admin_mode': admin_mode,
               'query_string': get_data.urlencode(),
               }
    return render(request, 'onlineshop/list.html', context)


def produit_detail(request, id):
    produit = get_object_or_404(Produit, id=id, available=True)
    cart_produit_form = CartAddProduitForm
    context = {
        'produit': produit,
        'cart_produit_form': cart_produit_form,
        'previous_page': 'onlineshop:produit-list',
    }
    return render(request, 'onlineshop/detail.html', context)


# ****************************************************************************************************************
# ADMINISTRATION
# ****************************************************************************************************************
@login_required
@staff_member_required
def onlineshop_administration(request):
    context = {}
    if request.user.is_staff:
        return render(request, 'onlineshop/administration_menu_onlineshop.html', context)
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('produit-list')


# PRODUITS *****************************************************************************************************
@login_required
@staff_member_required
def manage_produit(request):
    form = SearchProduitForm(request.GET or None)

    if request.user.is_staff:

        if 'p' in request.GET:
            order_value = request.GET['p']
            if order_value == 'total':
                queryset = Produit.objects.annotate(sum=Sum('Cartdbs__qte')).order_by('-sum')
            else:
                queryset = Produit.objects.all().order_by(order_value)
            request.session['p'] = request.GET['p']
        elif 'p' in request.session:
            order_value = request.session['p']
            if order_value == 'total':
                queryset = Produit.objects.annotate(sum=Sum('Cartdbs__qte')).order_by('-sum')
            else:
                queryset = Produit.objects.all().order_by(order_value)
        else:
            queryset = Produit.objects.all().order_by('variete', 'espece', 'portegreffe')

        if request.method == 'GET':
            if form.is_valid():
                espece = form.cleaned_data['especes']
                variete = form.cleaned_data['varietes']
                portegreffe = form.cleaned_data['portegreffes']
                spec = form.cleaned_data['specs']
                stock = form.cleaned_data['stock']
                gaf = form.cleaned_data['gaf']

                if not espece is None:
                    queryset = queryset.filter(espece=espece)
                if not variete is None:
                    queryset = queryset.filter(variete=variete)
                if not portegreffe is None:
                    queryset = queryset.filter(portegreffe=portegreffe)
                if not spec is None:
                    queryset = queryset.filter(spec=spec)
                if stock is True:
                    queryset = queryset.filter(stock_bis__gt=0)
                if gaf is True:
                    queryset = queryset.filter(gaf=True)

        title = "Produits"
        header = "Ajouter un Produit"
        javascript = "Cela va supprimer le produit"
        formAction = "onlineshop:manage-produit"
        previous_page = reverse('onlineshop:onlineshop-administration')

        paginator = Paginator(queryset, 50)
        get_data = request.GET.copy()
        page = get_data.pop('page', None)
        p = get_data.pop('p', None)
        if 'page' in request.GET:
            page = request.GET['page']
            request.session['page_p'] = page
        elif 'page_p' in request.session:
            page = request.session['page_p']

        try:
            produits = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            produits = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            produits = paginator.page(paginator.num_pages)

        context_header = {
            'header': header,
            'javascript': javascript,
        }
        context = {
            'produits': produits,
            'produits_list': queryset,
            'paginate': True,
            'previous_page': previous_page,
            'title': title,
            'context_header': context_header,
            'formAction': formAction,
            'form': form,
            'query_string': get_data.urlencode(),
        }

        return render(request, 'onlineshop/manage_produit.html', context)
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('onlineshop:produit-list')


@login_required
@staff_member_required
def add_produit(request):
    if request.user.is_staff:
        title = "Espèces"
        form = FormProduit(request.POST or None)
        message = "Produit ajouté avec succès !"

        previous_page = reverse('onlineshop:manage-produit')
        formAction = 'onlineshop:add-produit'

        if request.POST:
            if form.is_valid():
                instance = form.instance
                stock = instance.stock
                if stock is None or stock < 0 or not str(stock).isnumeric():
                    instance.stock = 0
                    instance.stock_bis = 0
                    instance.stock_Future = 0
                else:
                    instance.stock_bis = stock
                    instance.stock_future = stock
                instance.save()
                # try:

                # except:
                #     messages.error(request, "Un problème est survenue. Meri de réessayer")

                messages.success(request, message)
                return redirect('onlineshop:manage-produit')
        context_header = {
        }
        context = {
            'form': form,
            'formAction': formAction,
            'previous_page': previous_page,
            'title': title,
            'context_header': context_header,
        }
        return render(request, "onlineshop/form_produit.html", context)
    else:
        return redirect('produit-list')


@login_required
@staff_member_required
def edit_produit(request, produit_id):
    # RECUPERATION DES INFOS SELON CATEGORIE SI ADMIN CONNECTE
    if request.user.is_staff:
        title = "Produits"
        produit = Produit.objects.get(id=produit_id)
        form = FormProduit(request.POST or None, instance=produit)
        message = "Produit modifié avec succès !"

        previous_page = reverse('onlineshop:manage-produit')
        formAction = 'onlineshop:edit-produit', produit_id

        if request.POST:
            if form.is_valid():
                instance = form.instance
                stock = instance.stock
                if stock is None or stock < 0 or not str(stock).isnumeric():
                    instance.stock = 0
                    instance.stock_bis = 0
                    instance.stock_future = 0
                else:
                    instance.stock_bis = stock
                    instance.stock_future = stock
                obj = instance.save()
                messages.success(request, message)
                return redirect('onlineshop:manage-produit')
        context = {
            'produit_id': produit_id,
            'produit': produit,
            'formAction': formAction,
            'form': form,
            'previous_page': previous_page,
            'title': title,
        }
        return render(request, "onlineshop/form_produit.html", context)
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('produit-list')


@login_required
@staff_member_required
def delete_produit(request, produit_id):
    if request.user.is_staff:
        title = "Produits"
        produit = Produit.objects.get(id=produit_id)
        form = FormProduit(request.POST or None, instance=produit)
        message = "Produit supprimé avec succès !"

        produit.delete()
        messages.success(request, message)
        return redirect('onlineshop:manage-produit')
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('produit-list')


@login_required
@staff_member_required
def manage_greffons(request):
    form = SearchGreffonsForm(request.GET or None)
    couleurs = Couleur.objects.all()
    inventaires = Inventaire.objects.all()

    if request.user.is_staff:

        if 'g' in request.GET:
            order_value = request.GET['g']
            queryset = Greffons.objects.all().order_by(order_value)
            request.session['g'] = request.GET['g']
        elif 'g' in request.session:
            order_value = request.session['g']
            queryset = Greffons.objects.all().order_by(order_value)
        else:
            queryset = Greffons.objects.all().order_by('produit')

        if request.method == 'GET':
            print(form.errors)
            if form.is_valid():
                espece = form.cleaned_data['especes']
                variete = form.cleaned_data['varietes']
                portegreffe = form.cleaned_data['portegreffes']
                spec = form.cleaned_data['specs']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                couleur = form.cleaned_data['couleur']
                rang = form.cleaned_data['rang']
                inventaire = form.cleaned_data['inventaire']

                if espece is not None:
                    queryset = queryset.filter(produit__espece=espece)
                if variete is not None:
                    queryset = queryset.filter(produit__variete=variete)
                if portegreffe is not None:
                    queryset = queryset.filter(produit__portegreffe=portegreffe)
                if spec is not None:
                    queryset = queryset.filter(produit__spec=spec)
                if start_date is not None and start_date != "":
                    queryset = queryset.filter(date__gte=start_date)
                if end_date is not None and end_date != "":
                    queryset = queryset.filter(date__lte=end_date)
                if couleur.exists():
                    queryset = queryset.filter(couleur__in=couleur)
                if inventaire is not None:
                    queryset = queryset.filter(inventaire__in=inventaire)

        title = "Greffons"
        header = "Ajouter un Greffon"
        javascript = "Cela va supprimer le Greffon"
        formAction = "onlineshop:manage-greffons"
        previous_page = reverse('onlineshop:onlineshop-administration')

        paginator = Paginator(queryset, 50)
        get_data = request.GET.copy()
        page = get_data.pop('page', None)
        g = get_data.pop('g', None)
        if 'page' in request.GET:
            page = request.GET['page']
            request.session['page_g'] = page
        elif 'page_g' in request.session:
            page = request.session['page_p']

        try:
            greffons = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            greffons = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            greffons = paginator.page(paginator.num_pages)

        context_header = {
            'header': header,
            'javascript': javascript,
        }
        context = {
            'greffons': greffons,
            'greffons_list': queryset,
            'paginate': True,
            'previous_page': previous_page,
            'title': title,
            'context_header': context_header,
            'formAction': formAction,
            'form': form,
            'query_string': get_data.urlencode(),
            'couleurs': couleurs,
            'inventaires': inventaires,
        }

        return render(request, 'onlineshop/manage_greffons.html', context)
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('onlineshop:produit-list')

@login_required
@staff_member_required
def valid_greffons(request):
    greffons = Greffons.objects.all()
    pass


@login_required
@staff_member_required
def add_greffon(request):
    if request.user.is_staff:
        title = "Greffons"
        form = FormGreffon(request.POST or None)
        message = "Greffon ajouté avec succès !"

        previous_page = reverse('onlineshop:manage-greffons')
        formAction = 'onlineshop:add-greffon'

        if request.POST:
            if form.is_valid():
                instance = form.instance
                greffons = instance.greffons
                comm = instance.comm
                objectif = instance.objectif
                realise = instance.realise
                reussi = instance.reussi

                if greffons is None or greffons == "":
                    instance.greffons = 0

                if comm is None or comm == "":
                    instance.comm = 0

                if objectif is None or objectif == "":
                    instance.objectif = 0

                if realise is None or realise == "":
                        instance.realise = 0

                if reussi is None or reussi == "":
                    instance.reussi = 0

                instance.save()
                messages.success(request, message)
                return redirect('onlineshop:manage-greffons')
        context_header = {
        }
        context = {
            'form': form,
            'formAction': formAction,
            'previous_page': previous_page,
            'title': title,
            'context_header': context_header,
        }
        return render(request, "onlineshop/form_greffon.html", context)
    else:
        return redirect('produit-list')


@login_required
@staff_member_required
def edit_greffon(request, greffon_id):
    # RECUPERATION DES INFOS SELON CATEGORIE SI ADMIN CONNECTE
    if request.user.is_staff:
        title = "Greffons"
        greffon = Greffons.objects.get(id=greffon_id)
        form = FormGreffon(request.POST or None, instance=greffon)
        message = "Greffon modifié avec succès !"

        previous_page = reverse('onlineshop:manage-greffons')
        formAction = 'onlineshop:edit-greffon', greffon_id

        if request.POST:
            if form.is_valid():
                instance = form.instance
                qte = instance.greffons
                comm = instance.comm
                realise = instance.realise
                objectif = instance.objectif
                reussi = instance.reussi
                rang = instance.rang
                couleur = instance.couleur
                date = instance.date

                instance.qte = 0 if qte is None or qte == "" else qte
                instance.comm = 0 if comm is None or comm == "" else comm
                instance.objectif = 0 if objectif is None or objectif == "" else objectif
                instance.realise = 0 if realise is None or realise == "" else realise
                instance.reussi = 0 if reussi is None or reussi == "" else reussi
                instance.date = date
                instance.couleur = couleur
                instance.rang = rang

                obj = instance.save()
                messages.success(request, message)
                return redirect('onlineshop:manage-greffons')
        context = {
            'greffon_id': greffon_id,
            'greffon': greffon,
            'formAction': formAction,
            'form': form,
            'previous_page': previous_page,
            'title': title,
        }
        return render(request, "onlineshop/form_greffon.html", context)
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('produit-list')


@login_required
@staff_member_required
def delete_greffon(request, greffon_id):
    if request.user.is_staff:
        title = "Greffons"
        greffon = Greffons.objects.get(id=greffon_id)
        form = FormGreffon(request.POST or None, instance=greffon)
        message = "Greffon supprimé avec succès !"

        greffon.delete()
        messages.success(request, message)
        return redirect('onlineshop:manage-greffons')
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('produit-list')


# MISE A JOUR DES STOCKS D'UN PRODUIT
@login_required
@staff_member_required
def edit_qte_greffon(request):
    if request.method == 'POST' and request.is_ajax:
        data_string = request.POST.get('json_data')
        data_dict = json.loads(data_string)
        try:
            greffon_id = data_dict['code']
            qte = data_dict['greffon']
            # comm = data_dict['comm']
            objectif = data_dict['objectif']
            realise = data_dict['realise']
            reussi = data_dict['reussi']
            rang = data_dict['rang']
            date = datetime.strptime(data_dict['date'], '%d/%m/%Y')
            couleur_id = data_dict['couleur']
            inventaire_id = data_dict['inventaire']
        except Exception as e:
            print(e)

        if couleur_id is None or couleur_id == "":
            couleur = None
        else:
            couleur = Couleur.objects.get(id=couleur_id)

        if inventaire_id is None or inventaire_id == "":
            inventaire = None
        else:
            inventaire = Inventaire.objects.get(id=inventaire_id)

        try:
            greffon = Greffons.objects.get(id=greffon_id)
        except:
            messages.error(request, "Le greffon n'existe pas !")
            return redirect('onlineshop:manage-greffons')

        try:
            greffon.greffon = int(qte)
            # greffon.comm = int(comm)
            greffon.objectif = int(objectif)
            greffon.realise = int(realise)
            greffon.reussi = int(reussi)
            greffon.rang = rang
            greffon.date = date
            greffon.couleur = couleur
            greffon.inventaire = inventaire
            greffon.save()
        except Exception as e:
            print(e)

        messages.success(request, "Infos mise à jour pour le greffon ;)")
    return redirect('onlineshop:manage-greffons')


@login_required
@staff_member_required
def manage_couleurs(request):
    couleurs = Couleur.objects.all()

    previous_page = reverse('onlineshop:onlineshop-administration')
    context = {
        'couleurs': couleurs,
        'title': 'Gestion des couleurs',
        'previous_page': previous_page,
    }
    return render(request, 'onlineshop/manage_couleurs.html', context)


# *************************************************************************************
# TVA (ADD/UPDATE/DELETE)
# *************************************************************************************
@login_required
@staff_member_required
def add_couleur(request):
    if request.user.is_staff:
        title = "AJOUTER UNE COULEUR"
        form = FormCouleur(request.POST or None)
        previous_page = reverse('onlineshop:manage-greffons')
        formAction = 'onlineshop:add-couleur'

        if request.method == 'POST':
            if form.is_valid():
                nom = form.cleaned_data['nom']
                couleur = form.cleaned_data['couleur']
                form.save()

                message = "Nouvelle couleur ajoutée avec succès !"
                messages.success(request, message)
            else:
                message = "Une erreur s'est produite"
                messages.error(request, message)
            return redirect('onlineshop:manage-couleurs')

        context_header = {
        }

        context = {
            'form': form,
            'formAction': formAction,
            'previous_page': previous_page,
            'title': title,
            'context_header': context_header,
        }
        return render(request, "onlineshop/form_couleur.html", context)
    else:
        return redirect('onlineshop:manage-couleurs')


@login_required
@staff_member_required
def edit_couleur(request, couleur_id):
    # RECUPERATION DES INFOS SELON CATEGORIE SI ADMIN CONNECTE
    if request.user.is_staff:
        title = "COULEUR"
        couleur = Couleur.objects.get(id=couleur_id)
        form = FormCouleur(request.POST or None, instance=couleur)

        previous_page = reverse('onlineshop:manage-couleurs')
        formAction = 'onlineshop:edit-couleur', couleur_id

        if request.POST:
            if form.is_valid():
                nom = form.cleaned_data['nom']
                couleur = form.cleaned_data['couleur']

                message = "Couleur moidifiée avec succès !"
                messages.success(request, message)
                instance = form.instance
                obj = instance.save()

                return redirect('onlineshop:manage-couleurs')
        context = {
            'couleur_id': couleur_id,
            'couleur': couleur,
            'formAction': formAction,
            'form': form,
            'previous_page': previous_page,
            'title': title,
        }
        return render(request, "onlineshop/form_couleur.html", context)
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('produit-list')


@login_required
@staff_member_required
def delete_couleur(request, couleur_id):
    if request.user.is_staff:
        try:
            couleur = Couleur.objects.get(id=couleur_id)
            couleur.delete()
            message = "Couleur supprimée avec succès !"
            messages.success(request, message)
            return redirect('onlineshop:manage-couleurs')
        except:
            message = "Couleur inexistante !"
            messages.error(request, message)
            return redirect('onlineshop:manage-couleurs')
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('produit-list')


# ESPECES / VARIETES / PORTE GREFFE / SPECS ************************************************************************************
@login_required
@staff_member_required
def manage_data(request, categorie):
    categories = ['espece', 'variete', 'portegreffe', 'spec']
    if categorie not in categories:
        messages.error(request, "La catégorie spécifiée n'existe pas !")
        return redirect('onlineshop:onlineshop-administration')

    if request.user.is_staff:
        if categorie == 'espece':
            title = "Espèces"
            datas = Espece.objects.all()
            header = "Ajouter une Espèce"
            javascript = "Cela va supprimer l'espèce"

        if categorie == 'variete':
            title = "Variétés"
            datas = Variete.objects.all()
            header = "Ajouter une Variété"
            javascript = "Cela va supprimer la variété"

        if categorie == 'portegreffe':
            title = "Porte-Greffe"
            datas = PorteGreffe.objects.all()
            header = "Ajouter un Porte-Greffe"
            javascript = "Cela va supprimer le porte-greffe"

        if categorie == 'spec':
            title = "Spécialités"
            datas = Spec.objects.all()
            header = "Ajouter une Spécialité"
            javascript = "Cela va supprimer la spécialité"

        previous_page = reverse('onlineshop:onlineshop-administration')

        context_header = {
            'header': header,
            'javascript': javascript,
        }
        context = {
            'categorie': categorie,
            'datas': datas,
            'previous_page': previous_page,
            'title': title,
            'context_header': context_header,
        }

        return render(request, 'onlineshop/manage_data.html', context)
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('produit-list')


@login_required
@staff_member_required
def add_data(request, categorie):
    categories = ['espece', 'variete', 'portegreffe', 'spec']
    if categorie not in categories:
        messages.error(request, "La catégorie spécifiée n'existe pas !")
        return redirect('onlineshop:onlineshop-administration')

    if request.user.is_staff:
        if categorie == 'espece':
            title = "Espèces"
            form = FormEspece(request.POST or None)
            message = "Espèce ajoutée avec succès !"

        if categorie == 'variete':
            title = "Variétés"
            form = FormVariete(request.POST or None)
            message = "Variété ajoutée avec succès !"

        if categorie == 'portegreffe':
            title = "Porte-Greffes"
            form = FormPorteGreffe(request.POST or None)
            message = "Porte-Greffe ajouté avec succès !"

        if categorie == 'spec':
            title = "Spécialités"
            form = FormSpec(request.POST or None)
            message = "Spécialité ajoutée avec succès !"

        previous_page = reverse('onlineshop:manage-data', kwargs={'categorie': categorie})
        formAction = 'onlineshop:add-data', categorie

        if request.POST:
            if form.is_valid():
                obj = form.save()
                messages.success(request, message)
                return redirect('onlineshop:manage-data', categorie)
        context_header = {
        }
        context = {
            'form': form,
            'previous_page': previous_page,
            'formAction': formAction,
            'categorie': categorie,
            'title': title,
            'context_header': context_header,
        }
        return render(request, "onlineshop/form_data.html", context)
    else:

        return redirect('produit-list')


@login_required
@staff_member_required
def edit_data(request, categorie, data_id):
    # TEST SI CATEGORIE EXISTE
    categories = ['espece', 'variete', 'portegreffe', 'spec']
    if categorie not in categories:
        messages.error(request, "La catégorie spécifiée n'existe pas !")
        return redirect('onlineshop:onlineshop-administration')

    # RECUPERATION DES INFOS SELON CATEGORIE SI ADMIN CONNECTE
    if request.user.is_staff:
        if categorie == 'espece':
            title = "Espèces"
            data = Espece.objects.get(id=data_id)
            form = FormEspece(request.POST or None, instance=data)
            message = "Espèce modifiée avec succès !"

        if categorie == 'variete':
            title = "Variétés"
            data = Variete.objects.get(id=data_id)
            form = FormVariete(request.POST or None, instance=data)
            message = "Variété modifiée avec succès !"

        if categorie == 'portegreffe':
            title = "Porte-Greffes"
            data = PorteGreffe.objects.get(id=data_id)
            form = FormPorteGreffe(request.POST or None, instance=data)
            message = "Porte-Greffe modifiée avec succès !"

        if categorie == 'spec':
            title = "Spécialités"
            data = Spec.objects.get(id=data_id)
            form = FormSpec(request.POST or None, instance=data)
            message = "Spécialité modifiée avec succès !"

        previous_page = reverse('onlineshop:manage-data', kwargs={'categorie': categorie})
        formAction = 'onlineshop:edit-data', categorie, data_id

        if request.POST:
            if form.is_valid():
                obj = form.save()
                messages.success(request, message)
                return redirect('onlineshop:manage-data', categorie)
        context = {
            'data_id': data_id,
            'data': data,
            'formAction': formAction,
            'form': form,
            'previous_page': previous_page,
            'categorie': categorie,
            'title': title,
        }
        return render(request, "onlineshop/form_data.html", context)
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('produit-list')


@login_required
@staff_member_required
def delete_data(request, categorie, data_id):
    categories = ['espece', 'variete', 'portegreffe', 'spec']
    if categorie not in categories:
        messages.error(request, "La catégorie spécifiée n'existe pas !")
        return redirect('onlineshop:onlineshop-administration')

    if request.user.is_staff:
        if categorie == 'espece':
            title = "Espèces"
            data = Espece.objects.get(id=data_id)
            form = FormEspece(request.POST or None, instance=data)
            message = "Espèce supprimée avec succès !"
        if categorie == 'variete':
            title = "Variétés"
            data = Variete.objects.get(id=data_id)
            form = FormVariete(request.POST or None, instance=data)
            message = "Variété supprimée avec succès !"
        if categorie == 'portegreffe':
            title = "Porte-Greffes"
            data = PorteGreffe.objects.get(id=data_id)
            form = FormPorteGreffe(request.POST or None, instance=data)
            message = "Porte-Greffe supprimé avec succès !"
        if categorie == 'spec':
            title = "Spécialités"
            data = Spec.objects.get(id=data_id)
            form = FormSpec(request.POST or None, instance=data)
            message = "Spécialité supprimée avec succès !"

        data.delete()
        messages.success(request, message)
        return redirect('onlineshop:manage-data', categorie)
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('produit-list')


# ----------------------------------------------------------------------------------------------------------------------------------------
# MANAGE GLOBAL
# ----------------------------------------------------------------------------------------------------------------------------------------
@login_required
@staff_member_required
def export_produits_xls(request):
    output = io.BytesIO()

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(output)
    worksheet_produits = workbook.add_worksheet("PRODUITS")
    worksheet_especes = workbook.add_worksheet("ESPECES")
    worksheet_varietes = workbook.add_worksheet("VARIETES")
    worksheet_portegreffes = workbook.add_worksheet("PORTE-GREFFES")
    worksheet_specialites = workbook.add_worksheet("SPECIALITES")

    # PRODUITS
    worksheet_produits.write(0, 0, 'ID')
    worksheet_produits.write(0, 1, 'NOM')
    worksheet_produits.write(0, 2, 'SLUG')
    worksheet_produits.write(0, 3, 'DESCRIPTION')
    worksheet_produits.write(0, 4, 'PRIX')
    worksheet_produits.write(0, 5, 'STOCK')
    worksheet_produits.write(0, 6, 'STOCK BIS')
    worksheet_produits.write(0, 7, 'AVAILABLE')
    worksheet_produits.write(0, 8, 'ESPECE')
    worksheet_produits.write(0, 9, 'VARIETE')
    worksheet_produits.write(0, 10, 'PORTEGREFFE')
    worksheet_produits.write(0, 11, 'SPEC')
    worksheet_produits.write(0, 12, 'GAF')

    produits = Produit.objects.all()
    row = 1
    for produit in produits:
        worksheet_produits.write(row, 0, produit.id)
        worksheet_produits.write(row, 1, produit.nom)
        worksheet_produits.write(row, 2, produit.slug)
        worksheet_produits.write(row, 3, produit.description)
        worksheet_produits.write(row, 4, produit.prix)
        worksheet_produits.write(row, 5, produit.stock)
        worksheet_produits.write(row, 6, produit.stock_bis)
        worksheet_produits.write(row, 7, produit.available)
        worksheet_produits.write(row, 8, produit.espece.id)
        worksheet_produits.write(row, 9, produit.variete.id)
        worksheet_produits.write(row, 10, produit.portegreffe.id)
        if not produit.spec is None:
            worksheet_produits.write(row, 11, produit.spec.id)
        worksheet_produits.write(row, 12, produit.gaf)

        row += 1

    # ESPECES
    worksheet_especes.write(0, 0, 'ID')
    worksheet_especes.write(0, 1, 'NOM')
    worksheet_especes.write(0, 2, 'SLUG')

    produits = Espece.objects.all()
    row = 1
    for produit in produits:
        worksheet_especes.write(row, 0, produit.id)
        worksheet_especes.write(row, 1, produit.nom)
        worksheet_especes.write(row, 2, produit.slug)
        row += 1

    # VARIETES
    worksheet_varietes.write(0, 0, 'ID')
    worksheet_varietes.write(0, 1, 'NOM')
    worksheet_varietes.write(0, 2, 'SLUG')

    produits = Variete.objects.all()
    row = 1
    for produit in produits:
        worksheet_varietes.write(row, 0, produit.id)
        worksheet_varietes.write(row, 1, produit.nom)
        worksheet_varietes.write(row, 2, produit.slug)
        row += 1

    # PORTEGREFFES
    worksheet_portegreffes.write(0, 0, 'ID')
    worksheet_portegreffes.write(0, 1, 'NOM')
    worksheet_portegreffes.write(0, 2, 'SLUG')

    produits = PorteGreffe.objects.all()
    row = 1
    for produit in produits:
        worksheet_portegreffes.write(row, 0, produit.id)
        worksheet_portegreffes.write(row, 1, produit.nom)
        worksheet_portegreffes.write(row, 2, produit.slug)
        row += 1

    # SPECS
    worksheet_specialites.write(0, 0, 'ID')
    worksheet_specialites.write(0, 1, 'NOM')
    worksheet_specialites.write(0, 2, 'SLUG')

    produits = Spec.objects.all()
    row = 1
    for produit in produits:
        worksheet_specialites.write(row, 0, produit.id)
        worksheet_specialites.write(row, 1, produit.nom)
        worksheet_specialites.write(row, 2, produit.slug)
        row += 1

    workbook.close()
    output.seek(0)

    filename = 'ExportProduits.xlsx'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response


@login_required
@staff_member_required
def export_produits_xls_custom(request):
    output = io.BytesIO()

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(output)
    worksheet_produits = workbook.add_worksheet("PRODUITS")

    # PRODUITS
    worksheet_produits.write(0, 0, 'ID')
    worksheet_produits.write(0, 1, 'NOM')
    worksheet_produits.write(0, 2, 'DESCRIPTION')
    worksheet_produits.write(0, 3, 'PRIX')
    worksheet_produits.write(0, 4, 'STOCK')
    worksheet_produits.write(0, 5, 'STOCK BIS')
    worksheet_produits.write(0, 6, 'AVAILABLE')
    worksheet_produits.write(0, 7, 'ESPECE')
    worksheet_produits.write(0, 8, 'VARIETE')
    worksheet_produits.write(0, 9, 'PORTEGREFFE')
    worksheet_produits.write(0, 10, 'SPEC')
    worksheet_produits.write(0, 11, 'GAF')

    produits = Produit.objects.all()

    row = 1
    for produit in produits:
        worksheet_produits.write(row, 0, produit.id)
        worksheet_produits.write(row, 1, produit.nom)
        worksheet_produits.write(row, 2, produit.description)
        worksheet_produits.write(row, 3, produit.prix)
        worksheet_produits.write(row, 4, produit.stock)
        worksheet_produits.write(row, 5, produit.stock_bis)
        worksheet_produits.write(row, 6, produit.available)
        worksheet_produits.write(row, 7, produit.espece.nom)
        worksheet_produits.write(row, 8, produit.variete.nom)
        worksheet_produits.write(row, 9, produit.portegreffe.nom)
        if not produit.spec is None:
            worksheet_produits.write(row, 10, produit.spec.nom)
        worksheet_produits.write(row, 11, produit.gaf)

        row += 1

    workbook.close()
    output.seek(0)

    filename = 'ExportProduitsCustom.xlsx'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response


# IMPORT DES PRODUITS A PARTIR D'UN FICHIER EXCEL
@login_required
@staff_member_required
def import_produits_xls(request):

    previous_page = reverse('onlineshop:onlineshop-administration')

    try:
        if request.method == 'POST' and request.FILES['myfile']:
            myfile = request.FILES['myfile']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            excel_file = uploaded_file_url
            categorie = request.POST.get('categorie')
            message = ""

            wb = load_workbook(filename=settings.CONTENT_DIR + excel_file, read_only=True)
            ws = wb[categorie]
            max_col = ws.max_column
            max_row = ws.max_row
            print(max_row)

            # REMOVE DATA FROM TABLE PRODUITS
            if request.POST.get('delete_data', True):
                if categorie == "PRODUITS":
                    Produit.objects.all().delete()
                if categorie == "ESPECES":
                    Espece.objects.all().delete()
                if categorie == "VARIETES":
                    Variete.objects.all().delete()
                if categorie == "PORTE-GREFFES":
                    PorteGreffe.objects.all().delete()
                if categorie == "SPECIALITES":
                    Spec.objects.all().delete()

            for i in range(2, max_row + 1):
                if categorie == "PRODUITS":
                    obj = Produit.objects.create(
                        id=ws.cell(row=i, column=1).value,
                        nom=ws.cell(row=i, column=2).value,
                        slug=ws.cell(row=i, column=3).value,
                        description=ws.cell(row=i, column=4).value,
                        prix=ws.cell(row=i, column=5).value,
                        stock=ws.cell(row=i, column=6).value,
                        stock_bis=ws.cell(row=i, column=7).value,
                        available=ws.cell(row=i, column=8).value,
                        espece=get_object_from_id(ws.cell(row=i, column=9).value, 'espece'),
                        variete=get_object_from_id(ws.cell(row=i, column=10).value, 'variete'),
                        portegreffe=get_object_from_id(ws.cell(row=i, column=11).value, 'portegreffe'),
                        spec=get_object_from_id(ws.cell(row=i, column=12).value, 'spec'),
                        gaf=ws.cell(row=i, column=13).value,
                    )
                    message = "Fichier de produits importé avec succès (" + str(max_row) + " produits importés)"

                if categorie == "ESPECES":
                    obj = Espece.objects.create(
                        id=ws.cell(row=i, column=1).value,
                        nom=ws.cell(row=i, column=2).value,
                        slug=ws.cell(row=i, column=3).value
                    )
                    message = "Fichier d'espèces importé avec succès (" + str(max_row) + " espèces importées)"

                if categorie == "VARIETES":
                    obj = Variete.objects.create(
                        id=ws.cell(row=i, column=1).value,
                        nom=ws.cell(row=i, column=2).value,
                        slug=ws.cell(row=i, column=3).value
                    )
                    message = "Fichier de variétés importé avec succès (" + str(max_row) + " varietés importées)"

                if categorie == "PORTE-GREFFES":
                    obj = PorteGreffe.objects.create(
                        id=ws.cell(row=i, column=1).value,
                        nom=ws.cell(row=i, column=2).value,
                        slug=ws.cell(row=i, column=3).value
                    )
                    message = "Fichier de porte-greffe importé avec succès (" + str(max_row) + " porte-greffes importés)"

                if categorie == "SPECIALITES":
                    obj = Spec.objects.create(
                        id=ws.cell(row=i, column=1).value,
                        nom=ws.cell(row=i, column=2).value,
                        slug=ws.cell(row=i, column=3).value
                    )
                    message = "Fichier de spécialités importé avec succès (" + str(max_row) + " spécialités importées)"

                obj.save()

            messages.success(request, message)
            wb.close()

            return render(request, 'onlineshop/import_produit.html', {'previous_page': previous_page})

    except Exception as identifier:
        message = format_html("Une erreur est survenue ... merci de réessayer !<br>[ <i>" + str(identifier) + "</i> ]")
        messages.error(request, message)
        print(identifier)

    return render(request, 'onlineshop/import_produit.html', {'previous_page': previous_page})
    # return response


@login_required
@staff_member_required
def reset_stock(request):
    cancel_statut = Statut.objects.get(nom='Annulée')
    done_statut = Statut.objects.get(nom='Terminée')
    inprogress_statut = Statut.objects.filter(nom='En cours')
    form_statut = Statut.objects.filter(nom__in=['Validée', 'En cours'])
    commandes = Commande.objects.exclude(statut__in=[cancel_statut, done_statut])
    context = {}

    if commandes.count() > 0:
        message = format_html("Impossible de réinitialiser les Stocks !<br>Certaines commandes ne sont pas terminées/annulées")
        messages.error(request, message)

        form = SearchOrderForm(
            initial={
                'statut': form_statut, })
        context = {
            'form': form,
            'formAction': 'order:manage-order',
            'previous_page': reverse('onlineshop:onlineshop-administration'),
        }
        return render(request, 'order/manage_order.html', context)
        # return redirect('order:manage-order')

    produits = Produit.objects.all()
    for produit in produits:
        produit.stock = 0
        produit.stock_bis = 0
        produit.stock_future = 0
        produit.save()

    message = format_html("Les stocks (initiaux, virtuels et futurs) ont bien été réinitalisés !")
    messages.success(request, message)

    return redirect('onlineshop:onlineshop-administration')


# MISE A JOUR DES STOCKS D'UN PRODUIT
@login_required
@staff_member_required
def edit_stock_produit(request):
    if request.method == 'POST' and request.is_ajax:
        data_string = request.POST.get('json_data')
        data_dict = json.loads(data_string)
        print(data_dict)

        produit_id = data_dict['produit_id']
        stock = data_dict['stock']
        stock_bis = data_dict['stock_bis']
        stock_future = data_dict['stock_future']

        try:
            produit = Produit.objects.get(id=produit_id)
        except:
            messages.error(request, "Le produit n'existe pas !")
            return redirect('onlineshop:manage-produit')

        produit.stock = int(stock)
        produit.stock_bis = int(stock_bis)
        produit.stock_future = int(stock_future)
        produit.save()
        messages.success(request, "Quantité mise à jour pour le produit ;)")
    return redirect('onlineshop:manage-produit')
