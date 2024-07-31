from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User

# import onlineshop.models
# from onlineshop.models import


class Tva(models.Model):
    objects = models.Manager()
    tva = models.DecimalField(max_digits=10, decimal_places=2, null=False, unique=True)
    active = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    def __str__(self):
        taux_tva = '%s %%' % (self.tva)
        return taux_tva


class Client(models.Model):
    objects = models.Manager()
    nom = models.CharField(max_length=250, db_index=True, null=False, blank=False)
    prenom = models.CharField(max_length=250, db_index=True, null=True, blank=True)
    societe = models.CharField(max_length=250, null=True, blank=True)
    adresse = models.TextField(blank=True, null=True)
    cp = models.CharField(max_length=5, blank=True, null=True)
    ville = models.CharField(max_length=250, blank=True, null=True)
    tel = models.CharField(max_length=20, blank=True, null=True)
    mail = models.CharField(max_length=250, blank=False, null=False)
    commentaire = models.TextField(blank=True, null=True)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True, null=True)
    activate = models.BooleanField(default=True)
    user = models.ForeignKey(User, related_name='Clients', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        full_data = '%s %s (%s)' % (self.nom, self.prenom, self.mail)
        return full_data

    def get_fullname(self):
        full_name = '%s %s' % (self.nom, self.prenom)
        return full_name.strip()


class Statut(models.Model):
    nom = models.CharField(max_length=100, db_index=True, null=False, blank=False, default='En cours')

    def __str__(self):
        return self.nom


class Frais(models.Model):
    objects = models.Manager()
    nom = models.CharField(max_length=250, db_index=True, null=False, blank=False)
    tva = models.ForeignKey(Tva, related_name='Frais', on_delete=models.CASCADE)

    def __str__(self):
        return self.nom


class Inventaire(models.Model):
    objects = models.Manager()
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField(default=datetime.now() + timedelta(days=360))
    actif = models.BooleanField(default=False)

    def __str__(self):
        if self.end_date is not None:
            return str(self.start_date.year) + " - " + str(self.end_date.year)
        else:
            return str(self.start_date.year) + " - Maintenant"


class Commande(models.Model):
    objects = models.Manager()
    date = models.DateTimeField(default=datetime.now)
    date_update = models.DateTimeField(default=datetime.now)
    date_valid = models.DateTimeField(default=datetime.now)
    client = models.ForeignKey(Client, related_name='Commandes', on_delete=models.CASCADE)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    statut = models.ForeignKey(Statut, related_name='Commandes', on_delete=models.CASCADE)
    tva = models.ForeignKey(Tva, related_name='Commandes', on_delete=models.CASCADE)
    frais = models.ForeignKey(Frais, related_name='Commandes', on_delete=models.SET_NULL, blank=True, null=True)
    montant_frais = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    inventaire = models.ForeignKey(Inventaire, related_name='Commandes', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return '%s - %s - %s' % (self.date, self.client.get_fullname(), self.statut)

    def total_avant_remise(self):
        obj = Commande.objects.all().select_related('Cartdbs')
        for qte in obj.qte.all():
            print(qte)

    def qte_item(self):
        items = Cartdb.objects.filter(commande=self)
        nb_item = len(items)
        # print(items)
        return nb_item


# Liste des produits commandés ... chaque produit appartient à une et une seule commande
class Cartdb(models.Model):
    objects = models.Manager()
    produit = models.ForeignKey('onlineshop.Produit', related_name='Cartdbs', on_delete=models.CASCADE)
    qte = models.IntegerField(default=1)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=15.00)
    commande = models.ForeignKey(Commande, related_name='Cartdbs', on_delete=models.CASCADE)

    def add_cartdb(self, produit, qte, prix, commande):
        cartdb = self.create(produit=produit, qte=qte, prix=prix, commande=commande)
        return cartdb


class AccessMode(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User, related_name='AccessModes', on_delete=models.CASCADE)
    admin = models.BooleanField(default=False)


class LogOrder(models.Model):
    objects = models.Manager()
    user = models.TextField()
    order = models.TextField()
    date = models.DateTimeField(auto_now=True)
    action = models.TextField()
    field = models.TextField()
    old_value = models.TextField()
    new_value = models.TextField()
