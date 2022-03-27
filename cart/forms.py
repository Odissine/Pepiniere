from django import forms
from django_select2.forms import Select2Widget, Select2MultipleWidget
from order.models import Client

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 100)]


class CartAddProduitForm(forms.Form):
    # qte = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    # qte = forms.IntegerField(min_value=1, initial=1)
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class CartValidForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.clients = kwargs.pop('clients', None)
        super(CartValidForm, self).__init__(*args, **kwargs)

        self.fields['clients'] = forms.ModelChoiceField(
            label="Clients",
            queryset=Client.objects.all(),
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Clients', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir un client'
        )

    class Meta:
        model = Client
        fields = ['clients']


class CartUpdateForm(forms.Form):
    qte = forms.IntegerField(min_value=1, initial=1)
    prix = forms.CharField(max_length=8)


class RemiseUpdateForm(forms.Form):
    remise = forms.DecimalField(decimal_places=2, max_digits=5)
