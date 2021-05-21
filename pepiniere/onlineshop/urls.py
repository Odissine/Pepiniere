from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'onlineshop'

urlpatterns = [path('', views.produit_list, name='produit_list'),
               path('<slug:espece_slug>/', views.produit_list, name='produit_list_by_espece'),
               path('<int:id>/<slug:slug>/', views.produit_detail, name='produit_detail'),
               path('<slug:espece_slug>/<slug:variete_slug>/', views.produit_list, name='produit_list_by_esp_var'),
               path('<slug:espece_slug>/<slug:variete_slug>/<slug:portegreffe_slug>/', views.produit_list, name='produit_list_by_esp_var_pg'),
               path('<slug:espece_slug>/<slug:variete_slug>/<slug:portegreffe_slug>/<slug:spec_slug>/', views.produit_list, name='produit_list_by_esp_var_pg_spec')
               ]
