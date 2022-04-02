from onlineshop.models import *
from order.models import *
from django.contrib.auth.models import User
from datetime import datetime


def get_object_from_id(id_object, model):
    val = None
    if id_object is None:
        val = None
    else:
        if model == 'espece':
            val = Espece.objects.get(id=id_object)
        if model == 'variete':
            val = Variete.objects.get(id=id_object)
        if model == 'portegreffe':
            val = PorteGreffe.objects.get(id=id_object)
        if model == 'spec':
            val = Spec.objects.get(id=id_object)
        if model == 'user':
            val = User.objects.get(id=id_object)
        if model == 'client':
            val = Client.objects.get(id=id_object)
        if model == 'statut':
            val = Statut.objects.get(id=id_object)
        if model == 'tva':
            val = Tva.objects.get(id=id_object)
        if model == 'frais':
            val = Frais.objects.get(id=id_object)
        if model == 'commande':
            val = Commande.objects.get(id=id_object)
        if model == 'produit':
            val = Produit.objects.get(id=id_object)
        if model == 'couleur':
            val = Couleur.objects.get(id=id_object)
        if model == 'inventaire':
            val = Inventaire.objects.get(id=id_object)
    return val


def get_qte_pre_commande(produit):
    inventaire = Inventaire.objects.get(actif=True)
    produit = Produit.objects.get(pk=produit)
    qte = produit.stock_future
    # items = Cartdb.objects.filter(commande__inventaire=inventaire, produit=produit, commande__statut__nom="Pré-commande")
    # for item in items:
    #     qte += item.qte
    return qte


def check_stock_value(stock):
    try:
        stock = int(stock)
    except:
        return None

    if stock < 0:
        return None

    if stock is None:
        return None

    return stock


def check_produit_exist(espece, variete, portegreffe, spec=None):
    produits = Produit.objects.filter(espece=espece, variete=variete, portegreffe=portegreffe, spec=spec)
    return len(produits)