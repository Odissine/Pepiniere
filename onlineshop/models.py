from datetime import datetime
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
import django.utils.timezone
from order.models import *


class Espece(models.Model):
    objects = models.Manager()
    nom = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, null=True)

    class Meta:
        ordering = ('nom',)
        verbose_name = 'espece'
        verbose_name_plural = 'especes'

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('onlineshop:produit-list_by_espece', args=[self.slug])


class Variete(models.Model):
    objects = models.Manager()
    nom = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, null=True)

    class Meta:
        ordering = ('nom',)
        verbose_name = 'variete'
        verbose_name_plural = 'varietes'

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('onlineshop:produit-list_by_variete', args=[self.slug])


class PorteGreffe(models.Model):
    objects = models.Manager()
    nom = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, null=True)

    class Meta:
        ordering = ('nom',)
        verbose_name = 'porte-greffe'
        verbose_name_plural = 'porte-greffes'

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('onlineshop:produit-list_by_portegreffe', args=[self.slug])


class Spec(models.Model):
    objects = models.Manager()
    nom = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, null=True)

    class Meta:
        ordering = ('nom',)
        verbose_name = 'specialité'
        verbose_name_plural = 'specialités'

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('onlineshop:produit-list_by_spec', args=[self.slug])


class Produit(models.Model):
    objects = models.Manager()
    espece = models.ForeignKey(Espece, related_name='Produits', on_delete=models.CASCADE)
    variete = models.ForeignKey(Variete, related_name='Produits', on_delete=models.CASCADE)
    portegreffe = models.ForeignKey(PorteGreffe, related_name='Produits', on_delete=models.CASCADE)
    spec = models.ForeignKey(Spec, related_name='Produits', on_delete=models.CASCADE, blank=True, null=True)
    nom = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, blank=True)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=15.00)
    stock = models.IntegerField(default=0)
    stock_bis = models.IntegerField(default=0)
    stock_future = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    gaf = models.BooleanField(default=False)

    class Meta:
        ordering = ('nom',)
        index_together = (('id', 'slug'),)
        verbose_name = 'produit'
        verbose_name_plural = 'produits'

    def __str__(self):
        return self.nom

    def get_espece(self):
        return self.espece

    def get_variete(self):
        return self.variete # {'nom': self.variete, 'slug': slugify(self.variete)}

    def get_portegreffe(self):
        return self.portegreffe

    def get_spec(self):
        return self.spec

    def get_absolute_url(self):
        return reverse('onlineshop:produit-detail', args=[self.id, self.slug])

    def get_prix(self):
        return self.prix


class Couleur(models.Model):
    objects = models.Manager()
    nom = models.CharField(max_length=255)
    couleur = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

    def get_hexa(self):
        return self.couleur


class Greffons(models.Model):
    objects = models.Manager()
    produit = models.ForeignKey(Produit, related_name='Greffons', on_delete=models.CASCADE)
    greffons = models.IntegerField(default=0, null=True)
    comm = models.IntegerField(null=True)
    objectif = models.IntegerField(default=0, null=True)
    realise = models.IntegerField(default=0, null=True)
    date = models.DateTimeField(default=datetime.now, null=True)
    couleur = models.ForeignKey(Couleur, related_name='Greffons', on_delete=models.SET_NULL, null=True)
    rang = models.IntegerField(default=0, null=True)
    reussi = models.IntegerField(default=0, null=True)
    inventaire = models.ForeignKey(Inventaire, related_name='Greffons', on_delete=models.CASCADE, null=True)


class ProduitTest(models.Model):
    objects = models.Manager()
    espece = models.ForeignKey(Espece, related_name='ProduitTests', on_delete=models.CASCADE)
    variete = models.ForeignKey(Variete, related_name='ProduitTests', on_delete=models.CASCADE)
    portegreffe = models.ForeignKey(PorteGreffe, related_name='ProduitTests', on_delete=models.CASCADE)
    spec = models.ForeignKey(Spec, related_name='ProduitTests', on_delete=models.CASCADE, blank=True, null=True)
    nom = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, blank=True)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=15.00)
    stock = models.IntegerField(default=0)
    stock_bis = models.IntegerField(default=0)
    # stock_future = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    gaf = models.BooleanField(default=False)

    class Meta:
        ordering = ('nom',)
        index_together = (('id', 'slug'),)
        verbose_name = 'produit'
        verbose_name_plural = 'produits'

    def __str__(self):
        return self.nom
