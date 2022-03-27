from django import template
from onlineshop.models import *
from order.models import *
from django.db.models import Sum, F

register = template.Library()


def total_qte(produit):
    inventaire = Inventaire.objects.get(start_date__lte=datetime.now(), end_date__gte=datetime.now())
    total_qte = Commande.objects.filter(Cartdbs__produit=produit, inventaire=inventaire).aggregate(sum=Sum('Cartdbs__qte'))['sum']

    if total_qte is None:
        total_qte = 0

    return total_qte


register.filter('total_qte', total_qte)
