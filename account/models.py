from django.db import models
from django.contrib.auth.models import User


class TokenLogin(models.Model):
    objects = models.Manager()
    token = models.CharField(max_length=255, null=False, unique=True)
    user = models.ForeignKey(User, related_name='TokenLogins', null=False, on_delete=models.CASCADE)


class Config(models.Model):
    objects = models.Manager()
    register = models.BooleanField(default=False)
