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


def qte_order(order_id):
    commande = Commande.objects.get(id=order_id)
    produits = Cartdb.objects.filter(commande=commande)
    qte = 0
    for produit in produits:
        qte += produit.qte
    return qte
register.filter('qte_order', qte_order)


def remise_order(order_id):
    commande = Commande.objects.get(id=order_id)
    produits = Cartdb.objects.filter(commande=commande)
    total = 0
    for produit in produits:
        total += (produit.prix * produit.qte)

    total_remise = total * commande.remise / 100
    return total_remise
register.filter('remise_order', remise_order)


def total_post_remise(order_id):
    commande = Commande.objects.get(id=order_id)
    produits = Cartdb.objects.filter(commande=commande)
    total = 0
    for produit in produits:
        total += (produit.prix * produit.qte)

    total_remise = total * commande.remise / 100
    total_post_remise = total - total_remise
    return total_post_remise
register.filter('total_post_remise', total_post_remise)


def total_ht(order_id):
    commande = Commande.objects.get(id=order_id)
    produits = Cartdb.objects.filter(commande=commande)
    total = 0
    for produit in produits:
        total += (produit.prix * produit.qte)
    if commande.remise > 0:
        total_remise = total * commande.remise / 100
        total_post_remise = total - total_remise
        total_ht = total_post_remise / (1 + commande.tva.tva / 100)
    else:
        total_ht = total / (1 + commande.tva.tva / 100)
    return total_ht
register.filter('total_ht', total_ht)


def total_tva(order_id):
    commande = Commande.objects.get(id=order_id)
    produits = Cartdb.objects.filter(commande=commande)
    total = 0
    for produit in produits:
        total += (produit.prix * produit.qte)

    if commande.remise > 0:
        total_remise = total * commande.remise / 100
        total_post_remise = total - total_remise
        total_tva = total_post_remise - (total_post_remise / (1 + commande.tva.tva / 100))
    else:
        total_tva = total - (total / (1 + commande.tva.tva / 100))
    return total_tva
register.filter('total_tva', total_tva)


def frais_ht(order_id):
    commande = Commande.objects.get(id=order_id)
    if commande.frais is None:
        frais_ht = 0
        return frais_ht

    frais = Frais.objects.get(id=commande.frais.id)
    frais_ht = commande.montant_frais / (1 + frais.tva.tva / 100)
    return frais_ht
register.filter('frais_ht', frais_ht)


def frais_tva(order_id):
    commande = Commande.objects.get(id=order_id)
    montant_frais = commande.montant_frais
    if montant_frais is None or commande.frais is None:
        frais_tva = 0
    else:
        frais_ht = montant_frais / (1 + commande.frais.tva.tva / 100)
        frais_tva = frais_ht - (frais_ht / (1 + commande.frais.tva.tva / 100))
    return frais_tva
register.filter('frais_tva', frais_tva)


def total_global_tva(order_id):
    frais = frais_tva(order_id)
    total = total_tva(order_id)

    total_global_tva = total + frais
    return total_global_tva
register.filter('total_global_tva', total_global_tva)


def total_global_ttc(order_id):
    total_ttc = total_post_remise(order_id)
    commande = Commande.objects.get(id=order_id)
    montant_frais = commande.montant_frais
    if montant_frais is None:
        montant_frais = 0
    total_global_ttc = total_ttc + montant_frais
    return total_global_ttc
register.filter('total_global_ttc', total_global_ttc)


def total_global_ht(order_id):
    tva = total_global_tva(order_id)
    total_ttc = total_global_ttc(order_id)

    total_global_ht = total_ttc - tva
    return total_global_ht
register.filter('total_global_ht', total_global_ht)