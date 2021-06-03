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
    list_display = ['nom', 'slug', 'prix', 'stock', 'available', 'espece', 'variete', 'portegreffe']
    list_filter = ['stock', 'available', 'prix']
    list_editable = ['prix', 'stock', 'available']
    prepopulated_fields = {'nom': ('espece','variete', 'portegreffe', 'spec'), 'slug': ('nom',)}
    list_per_page = 200
    search_fields = ('nom',)
