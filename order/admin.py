from django.contrib import admin
from .models import Client, Commande, Cartdb, Statut, Frais, Inventaire


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'adresse', 'cp', 'ville', 'tel', 'mail', 'commentaire', 'remise', 'user']
    list_display_links = ['nom', 'prenom', 'adresse', 'cp', 'ville', 'tel', 'mail', 'commentaire', 'remise', 'user']
    list_filter = ['ville', 'remise']
    search_fields = ('nom', 'prenom',)


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'statut', 'date_update', 'inventaire']
    list_display_links = ['id', 'date']
    list_filter = ['statut']
    list_editable = ['statut']
    list_per_page = 100


@admin.register(Cartdb)
class Cartdb(admin.ModelAdmin):
    list_display = ['qte', 'prix', 'produit', 'commande']
    list_display_links = ['produit']
    list_filter = ['commande']
    list_per_page = 100


@admin.register(Statut)
class Statut(admin.ModelAdmin):
    list_display = ['nom']
    list_display_links = ['nom']


@admin.register(Frais)
class Frais(admin.ModelAdmin):
    list_display = ['nom', 'tva']
    list_display_links = ['nom', 'tva']
    list_filter = ['tva']
    fieldsets = [
        (None, {'fields': ['nom', 'tva']})
    ]  # list columns


@admin.register(Inventaire)
class Inventaire(admin.ModelAdmin):
    list_display = ['start_date', 'end_date']
    fieldsets = [
        (None, {'fields': ['start_date', 'end_date']})
    ]
