from datetime import datetime
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
import django.utils.timezone
from order.models import *
from django.contrib.auth.models import User


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
    produit = models.ForeignKey(Produit, related_name='Greffons', on_delete=models.CASCADE, verbose_name="Produits")
    greffons = models.IntegerField(default=0, null=True, verbose_name="Greffons")
    comm = models.IntegerField(null=True, verbose_name="Pré-Commande")
    objectif = models.IntegerField(default=0, null=True, verbose_name="Objectifs")
    realise = models.IntegerField(default=0, null=True, verbose_name="Réalisés")
    date = models.DateTimeField(default=datetime.now, null=True, verbose_name="Date")
    couleur = models.ForeignKey(Couleur, related_name='Greffons', on_delete=models.SET_NULL, null=True)
    rang = models.IntegerField(default=0, null=True, verbose_name="Rang")
    reussi = models.IntegerField(default=0, null=True, verbose_name="Reussi")
    inventaire = models.ForeignKey(Inventaire, related_name='Greffons', on_delete=models.CASCADE, null=True, verbose_name="Inventaire")


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


class LogCart(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    user_text = models.TextField(null=True, blank=True)
    cart = models.TextField()
    order = models.TextField(null=True, blank=True)
    produit = models.TextField()
    date = models.DateTimeField(auto_now=True)
    action = models.TextField()
    field = models.TextField()
    old_value = models.TextField()
    new_value = models.TextField()


class LogProduit(models.Model):
    objects = models.Manager()
    user = models.TextField()
    produit = models.TextField()
    order = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    action = models.TextField()
    field = models.TextField()
    old_value = models.TextField()
    new_value = models.TextField()