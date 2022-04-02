from django import template
from onlineshop.models import *
from order.models import *
from django.db.models import Sum, F

register = template.Library()


def total_qte_inventaire(produit):
    inventaire = Inventaire.objects.get(actif=True)
    total_qte = Commande.objects.filter(Cartdbs__produit=produit, inventaire=inventaire).aggregate(sum=Sum('Cartdbs__qte'))['sum']

    if total_qte is None:
        total_qte = 0

    return total_qte


register.filter('total_qte_inventaire', total_qte_inventaire)


def total_qte_global(produit):
    total_qte = Commande.objects.filter(Cartdbs__produit=produit).aggregate(sum=Sum('Cartdbs__qte'))['sum']

    if total_qte is None:
        total_qte = 0

    return total_qte


register.filter('total_qte_global', total_qte_global)
