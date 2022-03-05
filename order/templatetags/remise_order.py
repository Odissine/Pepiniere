from django import template
from order.models import *
register = template.Library()


def remise_order(order_id):
    commande = Commande.objects.get(id=order_id)
    produits = Cartdb.objects.filter(commande=commande)
    total = 0
    for produit in produits:
        total += (produit.prix * produit.qte)

    total_remise = total * commande.remise / 100
    return total_remise

register.filter('remise_order', remise_order)
