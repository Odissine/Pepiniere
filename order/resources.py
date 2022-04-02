from import_export import resources
from .models import *


class CommandeResource(resources.ModelResource):
    class Meta:
        model = Commande


class ClientResource(resources.ModelResource):
    class Meta:
        model = Client


class UserResource(resources.ModelResource):
    class Meta:
        model = User


class ProduitsCommandeResource(resources.ModelResource):
    class Meta:
        model = Cartdb


class InventaireResource(resources.ModelResource):
    class Meta:
        model = Inventaire


class StatutResource(resources.ModelResource):
    class Meta:
        model = Statut


class FraisResource(resources.ModelResource):
    class Meta:
        model = Frais


class TvaResource(resources.ModelResource):
    class Meta:
        model = Tva
