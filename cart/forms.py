from django import forms
from order.models import Client

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 100)]


class CartAddProduitForm(forms.Form):
    # qte = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    # qte = forms.IntegerField(min_value=1, initial=1)
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class CartValidForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all())


class CartUpdateForm(forms.Form):
    qte = forms.IntegerField(min_value=1, initial=1)
    prix = forms.CharField(max_length=8)


class RemiseUpdateForm(forms.Form):
    remise = forms.DecimalField(decimal_places=2, max_digits=5)
