from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Espece(models.Model):
    objects = models.Manager()
    nom = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('nom',)
        verbose_name = 'espece'
        verbose_name_plural = 'especes'

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('onlineshop:produit_list_by_espece', args=[self.slug])


class Variete(models.Model):
    objects = models.Manager()
    nom = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('nom',)
        verbose_name = 'variete'
        verbose_name_plural = 'varietes'

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('onlineshop:produit_list_by_variete', args=[self.slug])


class PorteGreffe(models.Model):
    objects = models.Manager()
    nom = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('nom',)
        verbose_name = 'porte-greffe'
        verbose_name_plural = 'porte-greffes'

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('onlineshop:produit_list_by_portegreffe', args=[self.slug])


class Spec(models.Model):
    objects = models.Manager()
    nom = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('nom',)
        verbose_name = 'specialité'
        verbose_name_plural = 'specialités'

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('onlineshop:produit_list_by_spec', args=[self.slug])


class Produit(models.Model):
    objects = models.Manager()
    espece = models.ForeignKey(Espece, related_name='produits', on_delete=models.CASCADE)
    variete = models.ForeignKey(Variete, related_name='produits', on_delete=models.CASCADE)
    portegreffe = models.ForeignKey(PorteGreffe, related_name='produits', on_delete=models.CASCADE)
    spec = models.ForeignKey(Spec, related_name='produits', on_delete=models.CASCADE, blank=True, null=True)
    nom = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    # image = models.ImageField(upload_to='produits/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=15.00)
    stock = models.IntegerField(default=0)
    stock_bis = models.IntegerField(default=0)
    available = models.BooleanField(default=True)

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
        return reverse('onlineshop:produit_detail', args=[self.id, self.slug])

    def get_prix(self):
        return self.prix
