from django import forms


class OrderAddProduitOrder(forms.Form):
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
