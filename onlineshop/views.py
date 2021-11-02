from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Espece, Variete, PorteGreffe, Spec, Produit
from cart.forms import CartAddProduitForm
from account.decorators import unauthenticated_user
from account.decorators import allowed_users
from django.utils.text import slugify
from django.http import JsonResponse


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


def produit_list(request, espece_slug=None, variete_slug=None, portegreffe_slug=None, spec_slug=None):
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
    varietes = Variete.objects.all()
    portegreffes = PorteGreffe.objects.all()
    specs = Spec.objects.all()

    produits_list = Produit.objects.filter(available=True).order_by('espece', 'variete', 'portegreffe')

    if not request.user.is_authenticated:
        produits_list = produits_list.filter(stock_bis__gt=0)

    if espece_slug:
        espece = get_object_or_404(Espece, slug=espece_slug)
        produits_list = produits_list.filter(espece=espece)
        # varietes = create_tab_dict(produits_list, 'variete')

    if variete_slug:
        variete = get_object_or_404(Variete, slug=variete_slug)
        produits_list = produits_list.filter(variete=variete)
        # portegreffes = create_tab_dict(produits_list, 'portegreffe')

    if portegreffe_slug:
        portegreffe = get_object_or_404(PorteGreffe, slug=portegreffe_slug)
        produits_list = produits_list.filter(portegreffe=portegreffe)
        # specs = create_tab_dict(produits_list, 'spec')

    if spec_slug:
        spec = get_object_or_404(Spec, slug=spec_slug)
        produits_list = produits_list.filter(spec=spec)

    if stock_bool:
        produits_list = produits_list.filter(stock_bis__gt=0)

    paginator = Paginator(produits_list, 50)
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

    return render(request, 'onlineshop/list.html', context)


def produit_detail(request, id, slug):
    produit = get_object_or_404(Produit, id=id, slug=slug, available=True)
    cart_produit_form = CartAddProduitForm
    return render(request, 'onlineshop/detail.html', {'produit': produit, 'cart_produit_form': cart_produit_form})


# def page_not_found_view(request, exception):
#    return render(request, 'onlineshop/404.html')

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

    return render(request, 'onlineshop/export.html', context)