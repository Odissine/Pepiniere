from django.urls import path
from django.conf.urls import url
from order import views

app_name = 'order'

urlpatterns = [
    path('', views.order_list, name='order-list'),
    path('list/', views.order_list, name='order-list'),
    path('add/', views.order_update_add_product, name='order-update-add-product'),
    path('detail/<id>', views.order_detail, name='order-detail'),
    path('valid/<id>', views.order_valid, name='order-valid'),
    path('pre_valid/<id>', views.order_pre_valid, name='order-pre-valid'),
    path('accept/<id>', views.order_accept, name='order-accept'),
    path('updatepq/<id>', views.order_update_qte_prix, name='order-update-qte-prix'),
    path('updateremise/<id>', views.order_update_remise, name='order-update-remise'),
    path('updatefrais/<id>', views.order_update_frais, name='order-update-frais'),
    path('product/remove/<id>', views.order_product_remove, name='order-product-remove'),
    path('cancel/<id>', views.order_cancel, name='order-cancel'),
    path('end/<id>', views.order_end, name='order-end'),
    path('pre_create/<id>', views.pre_order_create, name='pre-order-create'),
    path('search/client/', views.order_search_client, name='order-search-client'),
    path('search/order/', views.order_search_order, name='order-search-order'),
    path('print/<id>', views.order_print, name='order-print'),
    path('etiquettes/', views.order_etiquettes, name='order-etiquettes'),
    path('etiquettes/print', views.print_etiquettes, name='print-etiquettes'),

    # ADMIN
    path("administration/", views.order_administration, name="order-administration"),

    # COMMANDES
    path("order/manage", views.manage_order, name="manage-order"),
    path("order/reset", views.reset_order, name="reset-order"),
    path('order/prevalidall/<action>', views.all_order_pre_valid, name='all-order-pre-valid'),
    path('order/add/<order_id>/<manage>', views.add_produit_order, name='add-produit-order'),
    path('order/edit/<order_id>', views.edit_order, name='edit-order'),
    path('order/edit/produit/<order_id>/<produit_id>', views.edit_produit_order, name='edit-produit-order'),
    path('order/delete/<order_id>', views.delete_order, name='delete-order'),
    path('order/cancel/<order_id>', views.cancel_order, name='cancel-order'),
    path('order/validate/<order_id>', views.validate_order, name='validate-order'),
    path('order/inprogress/<order_id>', views.in_progress_order, name='in-progress-order'),
    path('order/finish/<order_id>', views.finish_order, name='finish-order'),
    path('order/delete/produit/<order_id>/<produit_id>', views.delete_produit_order, name='delete-produit-order'),
    path('order/recycle/produit/<order_id>/<produit_id>', views.recycle_produit_order, name='recycle-produit-order'),
    path('order/check/<produit_id>', views.get_produit_stock, name='get-produit-stock'),

    # CLIENTS
    path("client/manage", views.manage_client, name="manage-client"),
    path('client/add/', views.add_client, name='add-client'),
    path('client/edit/<client_id>', views.edit_client, name='edit-client'),
    path('client/delete/<client_id>', views.delete_client, name='delete-client'),
    path('client/activate/<client_id>', views.activate_client, name='activate-client'),

    path('divers/manage/', views.manage_divers, name='manage-divers'),
    # TVA
    path('tva/add/', views.add_tva, name='add-tva'),
    path('tva/edit/<tva_id>', views.edit_tva, name='edit-tva'),
    path('tva/delete/<tva_id>', views.delete_tva, name='delete-tva'),
    path('tva/default/<tva_id>', views.default_tva, name='default-tva'),

    # FRAIS
    path('frais/add/', views.add_frais, name='add-frais'),
    path('frais/edit/<frais_id>', views.edit_frais, name='edit-frais'),
    path('frais/delete/<frais_id>', views.delete_frais, name='delete-frais'),

    # STATUT
    path('statut/add/', views.add_statut, name='add-statut'),
    path('statut/edit/<statut_id>', views.edit_statut, name='edit-statut'),
    path('statut/delete/<statut_id>', views.delete_statut, name='delete-statut'),

    # INVENTAIRE
    path("inventaire/manage", views.manage_inventaire, name="manage-inventaire"),
    path('inventaire/add/', views.add_inventaire, name='add-inventaire'),
    path('inventaire/edit/<inventaire_id>', views.edit_inventaire, name='edit-inventaire'),
    path('inventaire/delete/<inventaire_id>', views.delete_inventaire, name='delete-inventaire'),

    path('export_commandes/', views.export_commandes_xls, name='export-commandes-xls'),
    path('import_commandes/', views.import_commandes_xls, name='import-commandes-xls'),

    path('export_clients/', views.export_clients_xls, name='export-clients-xls'),
    path('import_clients/', views.import_clients_xls, name='import-clients-xls'),

    path('export_divers/', views.export_divers_xls, name='export-divers-xls'),
    path('import_divers/', views.import_divers_xls, name='import-divers-xls'),

]
