from django.forms import ModelForm
from .models import *
from django import forms
from django_select2.forms import Select2Widget, Select2MultipleWidget


# FORMULAIRE DEDIE AU MOTEUR DE RECHERCHE DE PRODUITS ------------------------------------------------------------------------
class SearchProduitForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.especes = kwargs.pop('especes', None)
        self.varietes = kwargs.pop('varietes', None)
        self.portegreffes = kwargs.pop('portegreffes', None)
        self.specs = kwargs.pop('specs', None)
        self.stock = kwargs.pop('stock', None)
        super(SearchProduitForm, self).__init__(*args, **kwargs)

        self.fields['especes'] = forms.ModelChoiceField(
            label="Espèces",
            queryset=Espece.objects.all(),
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Especes', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une espèce')

        self.fields['varietes'] = forms.ModelChoiceField(
            label="Variétés",
            queryset=Variete.objects.all(),
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Variétés', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une variété')

        self.fields['portegreffes'] = forms.ModelChoiceField(
            label="Porte-Greffes",
            queryset=PorteGreffe.objects.all(),
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Porte-Greffes', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir un porte-greffe')

        self.fields['specs'] = forms.ModelChoiceField(
            label="Spécialités",
            queryset=Spec.objects.all(),
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Spécialités', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une spécialités')

        self.fields['stock'] = forms.BooleanField(
            label='En stock',
            required=False,
            help_text='Produits en stock uniquement ?',
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked': False})
        )

        self.fields['gaf'] = forms.BooleanField(
            label='Greffe à façon',
            required=False,
            help_text='Produits greffés à la demande !',
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked': False})
        )

    class Meta:
        fields = ['especes', 'varietes', 'portegreffes', 'specs', 'stock', 'gaf']


# FORMULAIRE DEDIE A L'AJOUT/EDITION D'UNE ESPECE ------------------------------------------------------------------------
class FormEspece(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormEspece, self).__init__(*args, **kwargs)

        self.fields['nom'] = forms.CharField(
            label="Espèce",
            required=True,
            widget=forms.TextInput(attrs={'placeholder': 'Nom de l\'epèce', 'class': 'form-control'}),
            help_text='Saisir un nom d\'espèce')

    class Meta:
        model = Espece
        fields = ['nom']


# FORMULAIRE DEDIE A L'AJOUT/EDITION D'UNE VARIETE ------------------------------------------------------------------------
class FormVariete(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormVariete, self).__init__(*args, **kwargs)

        self.fields['nom'] = forms.CharField(
            label="Variété",
            required=True,
            widget=forms.TextInput(attrs={'placeholder': 'Nom de la variété', 'class': 'form-control'}),
            help_text='Saisir un nom de variété')

    class Meta:
        model = Variete
        fields = ['nom']


# FORMULAIRE DEDIE A L'AJOUT/EDITION D'UN PORTE GREFFE ------------------------------------------------------------------------
class FormPorteGreffe(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormPorteGreffe, self).__init__(*args, **kwargs)

        self.fields['nom'] = forms.CharField(
            label="Porte-Greffe",
            required=True,
            widget=forms.TextInput(attrs={'placeholder': 'Nom du porte-greffe', 'class': 'form-control'}),
            help_text='Saisir un nom de porte-greffe')

    class Meta:
        model = PorteGreffe
        fields = ['nom']


# FORMULAIRE DEDIE A L'AJOUT/EDITION D'UNE SEPCIALITE ------------------------------------------------------------------------
class FormSpec(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormSpec, self).__init__(*args, **kwargs)

        self.fields['nom'] = forms.CharField(
            label="Spécialité",
            required=True,
            widget=forms.TextInput(attrs={'placeholder': 'Nom de la spécialité', 'class': 'form-control'}),
            help_text='Saisir un nom de spécialité')

    class Meta:
        model = Spec
        fields = ['nom']

# FORMULAIRE DEDIE A L'AJOUT/EDITION D'UN PRODUIT ------------------------------------------------------------------------
class FormProduit(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormProduit, self).__init__(*args, **kwargs)

        self.fields['nom'] = forms.CharField(
            label="Nom du Produit",
            required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Nom du produit', 'class': 'form-control'}),
            help_text='Saisir un nom pour le produit.<br/>Si vide il prendra les valeurs suivantes : Espece-Variete-PorteGreffe')

        self.fields['espece'] = forms.ModelChoiceField(
            label="Espèces",
            queryset=Espece.objects.all(),
            required=True,
            widget=Select2Widget(attrs={'placeholder': 'Especes', 'class': 'form-control js-example-basic-single', 'required':''}),
            help_text='Choisir une espèce')

        self.fields['variete'] = forms.ModelChoiceField(
            label="Variétés",
            queryset=Variete.objects.all(),
            required=True,
            widget=Select2Widget(attrs={'placeholder': 'Variétés', 'class': 'form-control js-example-basic-single', 'required':''}),
            help_text='Choisir une variété')

        self.fields['portegreffe'] = forms.ModelChoiceField(
            label="Porte-Greffes",
            queryset=PorteGreffe.objects.all(),
            required=True,
            widget=Select2Widget(attrs={'placeholder': 'Porte-Greffes', 'class': 'form-control js-example-basic-single', 'required':''}),
            help_text='Choisir un porte-greffe')

        self.fields['spec'] = forms.ModelChoiceField(
            label="Spécialités",
            queryset=Spec.objects.all(),
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Spécialités', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une spécialités')

        self.fields['stock'] = forms.IntegerField(
            label="Stock Initial",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Stock du produit', 'class': 'form-control', 'value': 0}),
            help_text='Saisir une valeur pour le stock initial... <br/>Valeur par défaut : 0')

        self.fields['gaf'] = forms.BooleanField(
            label="Greffe à façon",
            required=False,
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked': False}),
            help_text='Ce produit ne sera pas visible aux clients et ne servira qu\'une fois !')

    class Meta:
        model = Produit
        fields = ['nom', 'espece', 'variete', 'portegreffe', 'spec', 'stock', 'gaf']


# FORMULAIRE DEDIE A L'UPLOAD DU FICHIER EXCEL DE LA LISTE DES PRODUITS ------------------------------------------------------------------------
class ImportProduitForm(forms.ModelForm):

    class Meta:
        model = Produit
        fields = ['id', 'nom', 'slug', 'description', 'prix', 'stock',	'stock_bis', 'available', 'espece',	'variete', 'portegreffe', 'spec']
