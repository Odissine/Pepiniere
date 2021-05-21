from django.db import models


class Client(models.Model):
    nom = models.CharField(max_length=250, db_index=True, null=False, blank=False)
    prenom = models.CharField(max_length=250, db_index=True, null=False, blank=False)
    adresse = models.TextField(blank=True)
    cp = models.CharField(max_length=5, blank=True)
    ville = models.CharField(max_length=250, blank=True)
    tel = models.CharField(max_length=20, blank=True)
    mail = models.CharField(max_length=250, blank=False)
    commentaire = models.TextField(blank=True)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True)

class Commande(models.Model):
    objects = models.Manager()
    date = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(Client, related_name='clients', on_delete=models.CASCADE)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    statut = models.CharField(max_length=200, db_index=True, null=False, blank=False, default='En cours')
