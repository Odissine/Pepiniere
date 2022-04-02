from import_export import resources
from onlineshop.models import *


class ProduitResource(resources.ModelResource):
    class Meta:
        model = Produit


class EspeceResource(resources.ModelResource):
    class Meta:
        model = Espece


class VarieteResource(resources.ModelResource):
    class Meta:
        model = Variete


class PorteGreffeResource(resources.ModelResource):
    class Meta:
        model = PorteGreffe


class SpecResource(resources.ModelResource):
    class Meta:
        model = Spec


class GreffonResource(resources.ModelResource):
    class Meta:
        model = Greffons


class CouleurResource(resources.ModelResource):
    class Meta:
        model = Couleur
