from django.db import models
from django.contrib.auth.models import User
from onlineshop.models import Produit


class Client(models.Model):
    objects = models.Manager()
    nom = models.CharField(max_length=250, db_index=True, null=False, blank=False)
    prenom = models.CharField(max_length=250, db_index=True, null=False, blank=False)
    adresse = models.TextField(blank=True)
    cp = models.CharField(max_length=5, blank=True)
    ville = models.CharField(max_length=250, blank=True)
    tel = models.CharField(max_length=20, blank=True)
    mail = models.CharField(max_length=250, blank=False)
    commentaire = models.TextField(blank=True)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True)
    user = models.ForeignKey(User, related_name='client', on_delete=models.SET_NULL, blank=True, null=True)

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
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    tva = models.DecimalField(max_digits=10, decimal_places=2, default=20.00)


class Commande(models.Model):
    objects = models.Manager()
    date = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, related_name='commande', on_delete=models.CASCADE)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    statut = models.ForeignKey(Statut, related_name='commande', on_delete=models.CASCADE)
    # statut = models.CharField(max_length=250, db_index=True, null=False, blank=False, default='En cours')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_update = models.DateTimeField(auto_now=True)
    tva = models.DecimalField(max_digits=10, decimal_places=2, default=10.00, blank=True)
    frais = models.ForeignKey(Frais, related_name='commande', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.client.get_fullname()

    def add_frais(self, frais):
        if frais is None:
            self.frais = None
        else:
            frais_obj = Frais.objects.get(pk=frais)
            self.frais = frais_obj
        self.save()

    def montant_total(self):
        montant_remise = float(self.total) * float(self.remise) / 100
        print(montant_remise)
        montant_frais = 0
        if not self.frais is None:
            montant_frais = self.frais.prix
        somme = float(self.total) - float(montant_remise) + float(montant_frais)
        return somme

    def qte_item(self):
        items = Cartdb.objects.filter(commande=self)
        nb_item = len(items)
        print(items)
        print(items)
        return nb_item

class Cartdb(models.Model):
    objects = models.Manager()
    produit = models.ForeignKey(Produit, related_name='cartdb', on_delete=models.CASCADE)
    qte = models.IntegerField(default=1)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=15.00)
    commande = models.ForeignKey(Commande, related_name='cartdb', on_delete=models.CASCADE)
    total_line = models.DecimalField(max_digits=10, decimal_places=2, default=15.00)

    def add_cartdb(self, produit, qte, prix, commande, total_line):
        cartdb = self.create(produit=produit, qte=qte, prix=prix, commande=commande, total_line=total_line)
        return cartdb

    # def total_line(self):
    #     total = self.prix * self.qte
    #     return total
    #
    # def __len__(self, commande):
    #     cartdb = Cartdb.objects.filter(commande=commande)
    #     return sum(item['qte'] for item in self.cartdb.values())
    #
    # def get_total_prix(self, commande):
    #     cartdb = Cartdb.objects.filter(commande=commande)
    #     return sum(Decimal(item['prix']) * Decimal(item['qte']) for item in self.cartdb.values())
