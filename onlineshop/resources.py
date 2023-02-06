from import_export import resources, fields, widgets
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
    comm = fields.Field(
        column_name='Pré-Commandes',
        attribute='comm',
    )
    greffons = fields.Field(
        column_name='Greffons',
        attribute='greffons',
    )
    objectif = fields.Field(
        column_name='Objectifs',
        attribute='objectif',
    )
    realise = fields.Field(
        column_name='Réalisés',
        attribute='realise',
    )
    reussi = fields.Field(
        column_name='Réussis',
        attribute='reussi',
    )
    # variete = fields.Field(
    #     column_name='Variete',
    #     attribute='produit__variete',
    #     widget=widgets.ForeignKeyWidget(VarieteResource, 'nom')
    # )
    # espece = fields.Field(
    #     column_name='Espece',
    #     attribute='produit__espece',
    #     widget=widgets.ForeignKeyWidget(EspeceResource, 'nom')
    # )
    # portegreffe = fields.Field(
    #     column_name='Porte Greffe',
    #     attribute='produit__portegreffe',
    #     widget=widgets.ForeignKeyWidget(PorteGreffeResource, 'nom')
    # )
    produit = fields.Field(
        column_name='Produits',
        attribute='produit',
        widget=widgets.ForeignKeyWidget(Produit, 'nom')
    )
    rang = fields.Field(
        column_name='Rangs',
        attribute='rang',
    )

    class Meta:
        model = Greffons
        fields = ('id', 'produit', 'comm', 'greffons', 'objectif', 'realise', 'reussi', 'rang')
        export_order = ['id', 'produit', 'comm', 'greffons', 'objectif', 'realise', 'reussi', 'rang']
        import_id_fields = ('id',)


class CouleurResource(resources.ModelResource):
    class Meta:
        model = Couleur
