from django.contrib import admin
from .models import Client, Commande, Cartdb, Statut, Frais


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'adresse', 'cp', 'ville', 'tel', 'mail', 'commentaire', 'remise', 'user']
    list_display_links = ['nom', 'prenom', 'adresse', 'cp', 'ville', 'tel', 'mail', 'commentaire', 'remise', 'user']
    list_filter = ['ville', 'remise']
    search_fields = ('nom', 'prenom',)

# @admin.register(Commande)
# class CommandeAdmin(admin.ModelAdmin):
#     list_display = ['date', 'remise', 'statut', 'date_update','tva']
#     list_display_links = ['date', 'remise', 'statut']
#     list_filter = ['statut']

# @admin.register(Cartdb)
# class Cartdb(admin.ModelAdmin):
#     list_display = ['qte', 'prix']
#     list_display_links = ['qte', 'prix']

@admin.register(Statut)
class Statut(admin.ModelAdmin):
    list_display = ['nom']
    list_display_links = ['nom']

@admin.register(Frais)
class Frais(admin.ModelAdmin):
    list_display = ['nom', 'prix', 'tva']
    list_display_links = ['nom', 'prix', 'tva']
    list_filter = ['tva']
    fieldsets = [
        (None, {'fields': ['nom', 'prix', 'tva']})
    ]  # list columns
