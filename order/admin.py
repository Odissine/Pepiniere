from django.contrib import admin
from .models import Client, Commande, Cartdb


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'adresse', 'cp', 'ville', 'tel', 'mail', 'commentaire', 'remise']
    list_display_links = ['nom', 'prenom', 'adresse', 'cp', 'ville', 'tel', 'mail', 'commentaire', 'remise']

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['date', 'remise', 'statut']
    list_display_links = ['date', 'remise', 'statut']

@admin.register(Cartdb)
class Cartdb(admin.ModelAdmin):
    list_display = ['qte', 'prix']
    list_display_links = ['qte', 'prix']