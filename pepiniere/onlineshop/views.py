from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Espece, Variete, PorteGreffe, Spec, Produit
from cart.forms import CartAddProduitForm
from account.decorators import unauthenticated_user
from account.decorators import allowed_users


#@unauthenticated_user
#@allowed_users(allowed_roles=['user'])
def produit_list(request, espece_slug=None, variete_slug=None, portegreffe_slug=None, spec_slug=None):
    espece = None
    variete = None
    portegreffe = None
    spec = None

    especes = Espece.objects.all()
    varietes = Variete.objects.all()
    portegreffes = PorteGreffe.objects.all()
    specs = Spec.objects.all()
    produits_list = Produit.objects.filter(available=True).order_by('-stock')

    if espece_slug:
        espece = get_object_or_404(Espece, slug=espece_slug)
        produits_list = produits_list.filter(espece=espece)
    if variete_slug:
        variete = get_object_or_404(Variete, slug=variete_slug)
        produits_list = produits_list.filter(variete=variete)
    if portegreffe_slug:
        portegreffe = get_object_or_404(PorteGreffe, slug=portegreffe_slug)
        produits_list = produits_list.filter(portegreffe=portegreffe)
    if spec_slug:
        spec = get_object_or_404(Spec, slug=spec_slug)
        produits_list = produits_list.filter(spec=spec)

    paginator = Paginator(produits_list, 21)
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
               'paginate': True
               }

    return render(request, 'onlineshop/list.html', context)


#@unauthenticated_user
def produit_detail(request, id, slug):
    produit = get_object_or_404(Produit, id=id, slug=slug, available=True)
    cart_produit_form = CartAddProduitForm
    return render(request, 'onlineshop/detail.html', {'produit': produit, 'cart_produit_form': cart_produit_form})