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
import pandas as pd
from openpyxl import load_workbook


@login_required
@staff_member_required
def full_admin(request):
    admin = AccessMode.objects.filter(user=request.user).first()
    if admin:
        if admin.admin is True:
            admin.admin = False
        else:
            admin.admin = True
        admin.save()
    else:
        AccessMode.objects.create(user=request.user, admin=True)

    test = AccessMode.objects.first()
    print(test.user)
    print(test.admin)

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


def produit_list(request, espece=None, variete=None, portegreffe=None, spec=None):
    espece = None
    variete = None
    portegreffe = None
    spec = None
    stock = True
    gaf = False
    admin_mode = AccessMode.objects.get(user=request.user)
    formAction = 'onlineshop:produit-list'

    form = SearchProduitForm(request.POST or None)

    queryset = Produit.objects.filter(available=True).order_by('espece', 'variete', 'portegreffe')

    if request.method == 'POST':
        if form.is_valid():
            espece = form.cleaned_data['especes']
            variete = form.cleaned_data['varietes']
            portegreffe = form.cleaned_data['portegreffes']
            spec = form.cleaned_data['specs']
            stock = form.cleaned_data['stock']
            gaf = form.cleaned_data['gaf']

    if request.method == 'POST':
        if form.is_valid():
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

    if not request.user.is_authenticated:
        stock = True
        gaf = False
        queryset = queryset.filter(gaf=False, stock_bis__gt=0)

    paginator = Paginator(queryset, 50)
    page = request.GET.get('page')

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
               'stock': stock,
               'paginate': True,
               'form': form,
               'formAction': formAction,
               'espece': espece,
               'variete': variete,
               'portegreffe': portegreffe,
               'spec': spec,
               'gaf': gaf,
               'admin_mode': admin_mode.admin,
               }

    return render(request, 'onlineshop/list.html', context)


def produit_detail(request, id):
    produit = get_object_or_404(Produit, id=id, available=True)
    cart_produit_form = CartAddProduitForm
    return render(request, './onlineshop/detail.html', {'produit': produit, 'cart_produit_form': cart_produit_form})


# def page_not_found_view(request, exception):
#    return render(request, '404.html')

def export_produits(request, espece_slug=None, variete_slug=None, portegreffe_slug=None, spec_slug=None):
    espece = None
    variete = None
    portegreffe = None
    spec = None
    stock_bool = True

    if request.method == "POST":
        # print(request.POST)
        if request.POST['espece']:
            espece_slug = request.POST['espece']
            # print(espece_slug)

        if request.POST['variete']:
            variete_slug = request.POST['variete']

        if request.POST['portegreffe']:
            portegreffe_slug = request.POST['portegreffe']

        if request.POST['spec']:
            spec_slug = request.POST['spec']

        stock_check = request.POST.get("stock_bool", None)
        if stock_check == "True":
            stock_bool = True
        else:
            stock_bool = False

    especes = Espece.objects.all()
    produits_list = Produit.objects.filter(available=True).order_by('espece', 'variete', 'portegreffe')

    if not request.user.is_authenticated:
        produits_list = produits_list.filter(stock_bis__gt=0)

    varietes = create_tab_dict(produits_list, 'variete')
    portegreffes = create_tab_dict(produits_list, 'portegreffe')
    specs = create_tab_dict(produits_list, 'spec')

    if espece_slug:
        espece = get_object_or_404(Espece, slug=espece_slug)
        produits_list = produits_list.filter(espece=espece)
        varietes = create_tab_dict(produits_list, 'variete')

    if variete_slug:
        variete = get_object_or_404(Variete, slug=variete_slug)
        produits_list = produits_list.filter(variete=variete)
        portegreffes = create_tab_dict(produits_list, 'portegreffe')

    if portegreffe_slug:
        portegreffe = get_object_or_404(PorteGreffe, slug=portegreffe_slug)
        produits_list = produits_list.filter(portegreffe=portegreffe)
        specs = create_tab_dict(produits_list, 'spec')

    if spec_slug:
        spec = get_object_or_404(Spec, slug=spec_slug)
        produits_list = produits_list.filter(spec=spec)

    if stock_bool:
        produits_list = produits_list.filter(stock_bis__gt=0)

    paginator = Paginator(produits_list, 5000)
    page = request.GET.get('page')

    try:
        produits = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        produits = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        produits = paginator.page(paginator.num_pages)

    context = {'espece': espece,
               'especes': especes,
               'variete': variete,
               'varietes': varietes,
               'portegreffe': portegreffe,
               'portegreffes': portegreffes,
               'spec': spec,
               'specs': specs,
               'produits': produits,
               'produits_list': produits_list,
               'stock_bool': stock_bool,
               'paginate': True
               }

    return render(request, './onlineshop/export.html', context)


# ****************************************************************************************************************
# ADMINISTRATION
# ****************************************************************************************************************
@login_required
def onlineshop_administration(request):
    context = {}
    if request.user.is_staff:
        return render(request, 'onlineshop/administration_menu_onlineshop.html', context)
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('produit-list')


# PRODUITS *****************************************************************************************************
def manage_produit(request):
    form = SearchProduitForm(request.POST or None)

    if request.user.is_staff:
        queryset = Produit.objects.all().order_by('espece', 'variete', 'portegreffe')
        if request.method == 'POST':
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
        page = request.GET.get('page')

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
            'paginate': True,
            'previous_page': previous_page,
            'title': title,
            'context_header': context_header,
            'formAction': formAction,
            'form': form,
        }

        return render(request, 'onlineshop/manage_produit.html', context)
    else:
        messages.error(request, "Vous n'avez pas les droits !")
        return redirect('onlineshop:produit-list')


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


# ESPECES / VARIETES / PORTE GREFFE / SPECS ************************************************************************************
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
        context['form'] = form
        context['formAction'] = 'order:manage-order'
        return render(request, 'order/manage_order.html', context)
        # return redirect('order:manage-order')

    produits = Produit.objects.all()
    for produit in produits:
        produit.stock = 0
        produit.stock_bis = 0
        produit.save()

    message = format_html("Les stocks initiaux et virtuels ont bien été réinitalisés !")
    messages.error(request, message)

    return redirect('onlineshop:onlineshop-administration')
