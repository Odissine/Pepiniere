from django.urls import path
from django.conf.urls import url
from onlineshop.views import *

app_name = 'onlineshop'

urlpatterns = [
    path('', produit_list, name='produit-list'),
    path('modeadmin/', full_admin, name='full-admin'),
    path('detail/<id>/', produit_detail, name='produit-detail'),

    # ADMINISTRATION ONLINESHOP
    path("administration/", onlineshop_administration, name="onlineshop-administration"),
    path('export_xls/', export_produits_xls, name='export-produits-xls'),
    path('export_xls_custom/', export_produits_xls_custom, name='export-produits-xls-custom'),
    path('import_xls/', import_produits_xls, name='import-produits-xls'),
    path('reset/', reset_stock, name='reset-stock'),

    # PRODUITS
    path('produits/manage', manage_produit, name='manage-produit'),
    path('produits/add', add_produit, name='add-produit'),
    path('produits/edit/<produit_id>', edit_produit, name='edit-produit'),
    path('produits/delete/<produit_id>', delete_produit, name='delete-produit'),
    path('produits/edit/stock/', edit_stock_produit, name='edit-stock-produit'),

    # GREFFONS
    path('greffons/manage', manage_greffons, name='manage-greffons'),
    path('greffons/add', add_greffon, name='add-greffon'),
    path('greffons/edit/<greffon_id>', edit_greffon, name='edit-greffon'),
    path('greffons/delete/<greffon_id>', delete_greffon, name='delete-greffon'),
    path('greffons/edit/qte/', edit_qte_greffon, name='edit-qte-greffon'),
    path('greffons/valid', valid_greffons, name='valid-greffon'),

    path('couleurs/manage', manage_couleurs, name='manage-couleurs'),
    path('couleurs/add', add_couleur, name='add-couleur'),
    path('couleurs/edit/<couleur_id>', edit_couleur, name='edit-couleur'),
    path('couleurs/delete/<couleur_id>', delete_couleur, name='delete-couleur'),

    # ESPECES / VARIETES / PORTEGREFFE / SPEC
    path('data/manage/<categorie>', manage_data, name='manage-data'),
    path('data/add/<categorie>', add_data, name='add-data'),
    path('data/edit/<categorie>/<data_id>', edit_data, name='edit-data'),
    path('data/delete/<categorie>/<data_id>', delete_data, name='delete-data'),
]
