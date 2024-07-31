from onlineshop.models import Greffons, Espece, Variete, PorteGreffe, Spec, Produit, Couleur, DataMapping
from order.models import Client, Statut, Tva, Frais, Commande, Inventaire, Cartdb
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Sum, F, ForeignKey
from django.apps import apps


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


def get_list_produits_anomalie(inventaire):
    produits = Produit.objects.all()
    annulee = Statut.objects.get(nom="Annulée")
    encours = Statut.objects.get(nom="En cours")
    validee = Statut.objects.get(nom="Validée")
    terminee = Statut.objects.get(nom="Terminée")
    anomalies = []
    data = []
    for produit in produits:
        qte = Cartdb.objects.filter(commande__inventaire=inventaire, produit=produit).exclude(commande__statut=annulee).aggregate(sum=Sum('qte'))['sum']
        qte_encours = Cartdb.objects.filter(commande__inventaire=inventaire, produit=produit, commande__statut__in=[encours, validee]).exclude(commande__statut=annulee).aggregate(sum=Sum('qte'))['sum']
        qte_termine = Cartdb.objects.filter(commande__inventaire=inventaire, produit=produit, commande__statut=terminee).exclude(commande__statut=annulee).aggregate(sum=Sum('qte'))['sum']
        # SF - QTE  != EN COURS
        if qte is not None:
            if qte_encours is None:
                qte_encours = 0
            if qte_termine is None:
                qte_termine = 0
            if (produit.stock + qte_termine) != (produit.stock_bis + qte_encours + qte_termine):
                anomalies.append(produit)
                data.append((produit.pk, produit.stock, produit.stock_bis, qte, qte_encours, qte_termine))
    return anomalies


def import_greffons(file):
    fields = Greffons._meta.get_fields()

    pass


def get_or_create_mappings(mappings):
    model_list = ['Greffons', 'Produit', 'Espece', 'Variete', 'PorteGreffe']
    # Result needed : {'model':{'name':['field']}}
    mapping_dict = {}
    for model in model_list:
        mapping_dict[model] = {}
        ModelClass = apps.get_model('onlineshop', model)
        fields = [field.name for field in ModelClass._meta.get_fields() if not field.one_to_many]

        for field in fields:
            mapping_dict[model][field] = []
            mapping_items = mappings.filter(model=model, name=field)
            if not mapping_items.exists():
                DataMapping.objects.create(name=field, field=field, model=model)
                mapping_dict[model][field].append(field)
            else:
                for mapping_item in mapping_items:
                    mapping_dict[model][field].append(mapping_item.field)



    return mapping_dict


