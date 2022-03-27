from onlineshop.models import *
from order.models import *
from django.contrib.auth.models import User


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
    return val
