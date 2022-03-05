from django.contrib import admin
from .models import Espece, Variete, PorteGreffe, Spec, Produit


@admin.register(Espece)
class EspeceAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug']
    prepopulated_fields = {'slug': ('nom',)}


@admin.register(Variete)
class VarieteAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug']
    prepopulated_fields = {'slug': ('nom',)}
    search_fields = ('nom',)


@admin.register(PorteGreffe)
class PorteGreffeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug']
    prepopulated_fields = {'slug': ('nom',)}


@admin.register(Spec)
class SpecAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug']
    prepopulated_fields = {'slug': ('nom',)}


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug', 'prix', 'stock', 'stock_bis', 'available', 'espece', 'variete', 'portegreffe', 'gaf']
    list_filter = ['available', 'prix', 'espece', 'portegreffe', 'gaf']
    list_editable = ['prix', 'stock', 'available', 'stock_bis', 'gaf']
    prepopulated_fields = {'nom': ('espece', 'variete', 'portegreffe', 'spec'), 'slug': ('nom',),}
    list_per_page = 200
    search_fields = ('nom',)
