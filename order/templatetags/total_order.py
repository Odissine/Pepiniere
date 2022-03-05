from django import template
from order.models import *
register = template.Library()


def total_order(order_id):
    commande = Commande.objects.get(id=order_id)
    produits = Cartdb.objects.filter(commande=commande)
    total = 0
    for produit in produits:
        total += (produit.prix * produit.qte)
    return total

register.filter('total_order', total_order)