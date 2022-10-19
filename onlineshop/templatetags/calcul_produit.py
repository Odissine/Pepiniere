from django import template
from onlineshop.models import *
from order.models import *
from django.db.models import Sum, F

register = template.Library()


def total_qte_inventaire(produit):
    statut_annulee = Statut.objects.get(nom="Annulée")
    inventaire = Inventaire.objects.get(actif=True)
    total_qte = Commande.objects.filter(Cartdbs__produit=produit, inventaire=inventaire).exclude(statut=statut_annulee).aggregate(sum=Sum('Cartdbs__qte'))['sum']

    if total_qte is None:
        total_qte = 0

    return total_qte


register.filter('total_qte_inventaire', total_qte_inventaire)


def total_qte_encours(produit):
    statut_encours = Statut.objects.get(nom="En cours")
    inventaire = Inventaire.objects.get(actif=True)
    total_qte = Commande.objects.filter(Cartdbs__produit=produit, inventaire=inventaire, statut=statut_encours).aggregate(sum=Sum('Cartdbs__qte'))['sum']

    if total_qte is None:
        total_qte = 0

    return total_qte


register.filter('total_qte_encours', total_qte_encours)


def total_qte_validee(produit):
    statut_validee = Statut.objects.get(nom="Validée")
    inventaire = Inventaire.objects.get(actif=True)
    total_qte = Commande.objects.filter(Cartdbs__produit=produit, inventaire=inventaire, statut=statut_validee).aggregate(sum=Sum('Cartdbs__qte'))['sum']

    if total_qte is None:
        total_qte = 0

    return total_qte


register.filter('total_qte_validee', total_qte_validee)


def total_qte_terminee(produit):
    statut_terminee = Statut.objects.get(nom="Terminée")
    inventaire = Inventaire.objects.get(actif=True)
    total_qte = Commande.objects.filter(Cartdbs__produit=produit, inventaire=inventaire, statut=statut_terminee).aggregate(sum=Sum('Cartdbs__qte'))['sum']

    if total_qte is None:
        total_qte = 0

    return total_qte


register.filter('total_qte_terminee', total_qte_terminee)


def total_qte_annulee(produit):
    statut_annulee= Statut.objects.get(nom="Annulée")
    inventaire = Inventaire.objects.get(actif=True)
    total_qte = Commande.objects.filter(Cartdbs__produit=produit, inventaire=inventaire, statut=statut_annulee).aggregate(sum=Sum('Cartdbs__qte'))['sum']

    if total_qte is None:
        total_qte = 0

    return total_qte


register.filter('total_qte_annulee', total_qte_annulee)


def total_qte_global(produit):
    statut_annulee = Statut.objects.get(nom="Annulée")
    total_qte = Commande.objects.filter(Cartdbs__produit=produit).exclude(statut=statut_annulee).aggregate(sum=Sum('Cartdbs__qte'))['sum']

    if total_qte is None:
        total_qte = 0

    return total_qte


register.filter('total_qte_global', total_qte_global)


def qte_commande_produit(produit, mode):
    annulee = Statut.objects.get(nom="Annulée")
    encours = Statut.objects.get(nom="En cours")
    validee = Statut.objects.get(nom="Validée")
    terminee = Statut.objects.get(nom="Terminée")
    inventaire = Inventaire.objects.get(actif=True)
    if mode == "c":
        qte = Cartdb.objects.filter(commande__inventaire=inventaire, produit=produit, commande__statut__in=[encours, validee]).exclude(commande__statut=annulee).aggregate(sum=Sum('qte'))['sum']

    if mode == "f":
        qte = Cartdb.objects.filter(commande__inventaire=inventaire, produit=produit, commande__statut=terminee).exclude(commande__statut=annulee).aggregate(sum=Sum('qte'))['sum']

    if qte is None:
        qte = 0

    return qte


register.filter('qte_commande_produit', qte_commande_produit)
