from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'order'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('list/', views.order_list, name='order_list'),
    path('add/', views.order_update_add_product, name='order_update_add_product'),
    path('detail/<int:id>', views.order_detail, name='order_detail'),
    path('valid/<int:id>', views.order_valid, name='order_valid'),
    path('update/<int:id>', views.order_update, name='order_update'),
    path('updatepq/<int:id>', views.order_update_qte_prix, name='order_update_qte_prix'),
    path('updateprice/<int:id>', views.order_update_price, name='order_update_price'),
    path('updateremise/<int:id>', views.order_update_remise, name='order_update_remise'),
    path('updatefrais/<int:id>', views.order_update_frais, name='order_update_frais'),
    path('remove/<int:id>', views.order_remove, name='order_remove'),
    path('cancel/<int:id>', views.order_cancel, name='order_cancel'),
    path('end/<int:id>', views.order_end, name='order_end'),
    path('search/client/', views.order_search_client, name='order_search_client'),
    path('search/order/', views.order_search_order, name='order_search_order'),
    path('print/<int:id>', views.order_print, name='order_print'),
    path('etiquettes/', views.order_etiquettes, name='order_etiquettes'),
    path('etiquettes/print', views.export_etiquettes, name='export_etiquettes'),
]
