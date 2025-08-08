from django.forms import ModelForm
from .models import *
from django import forms
from django_select2.forms import Select2Widget, Select2MultipleWidget
from logApp.views import *


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
            initial=True,
            help_text='Produits en stock uniquement ?',
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
        )

        self.fields['gaf'] = forms.BooleanField(
            label='Greffe à façon',
            required=False,
            help_text='Produits greffés à la demande !',
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked': False})
        )

    class Meta:
        fields = ['especes', 'varietes', 'portegreffes', 'specs', 'stock', 'gaf']


class SearchGreffonsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.especes = kwargs.pop('especes', None)
        self.varietes = kwargs.pop('varietes', None)
        self.portegreffes = kwargs.pop('portegreffes', None)
        self.specs = kwargs.pop('specs', None)
        self.date = kwargs.pop('date', None)
        self.couleur = kwargs.pop('couleur', None)
        self.inventaire = kwargs.pop('inventaire', None)
        super(SearchGreffonsForm, self).__init__(*args, **kwargs)

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

        self.fields['start_date'] = forms.DateField(
            label="Date de début du greffon",
            required=False,
            widget=forms.DateInput(attrs={'placeholder': 'Date du greffon', 'class': 'datepicker_input form-control'}),
            help_text='Séléctionner une date après laquelle les greffons ont été greffés',
        )
        self.fields['end_date'] = forms.DateField(
            label="Date de fin du greffon",
            required=False,
            widget=forms.DateInput(attrs={'placeholder': 'Date du greffon', 'class': 'datepicker_input form-control'}),
            help_text='Séléctionner une date avant laquelle les greffons ont été greffés',
        )
        self.fields['couleur'] = forms.ModelMultipleChoiceField(
            label="Couleurs",
            queryset=Couleur.objects.all(),
            required=False,
            widget=Select2MultipleWidget(attrs={'placeholder': 'Couleurs', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une couleur'
        )

        self.fields['inventaire'] = forms.ModelChoiceField(
            label="Période",
            queryset=Inventaire.objects.all(),
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Période', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une période')

    class Meta:
        fields = ['especes', 'varietes', 'portegreffes', 'specs', 'start_date', 'end_date', 'couleur', 'rang', 'inventaire']


class FormGreffon(forms.ModelForm):

    def __init__(self,  *args, **kwargs):
        self.produit = kwargs.pop('produit', None)
        self.greffons = kwargs.pop('greffons', None)
        self.comm = kwargs.pop('comm', None)
        self.objectif = kwargs.pop('objectif', None)
        self.realise = kwargs.pop('realise', None)
        self.reussi = kwargs.pop('reussi', None)
        self.date = kwargs.pop('date', None)
        self.couleur = kwargs.pop('couleur', None)
        self.rang = kwargs.pop('rang', None)
        self.inventaire = kwargs.pop('inventaire', None)
        super(FormGreffon, self).__init__(*args, **kwargs)

        inventaire_actif = Inventaire.objects.get(actif=True)

        self.fields['produit'] = forms.ModelChoiceField(
            label="Produits",
            queryset=Produit.objects.exclude(Greffons__inventaire=inventaire_actif),
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Produit', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir un produit dans la liste des produit existant !')

        self.fields['date'] = forms.DateField(
            label="Date du greffon",
            required=False,
            initial=datetime.now(),
            widget=forms.DateInput(attrs={'placeholder': 'Date du greffon', 'class': 'datepicker_input form-control'}),
            help_text='Saisir une date à laquelle le greffon a été réalisé',
        )
        self.fields['greffons'] = forms.CharField(
            label="Nombre de greffons",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Nombre de greffons', 'class': 'form-control'}),
            help_text='Quantité de greffon',
        )
        self.fields['comm'] = forms.CharField(
            label="Quantité de produits pré-commandés",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Quantité de produits pré-commandés', 'class': 'form-control'}),
            help_text='Quantité de produits pré-commandés',
        )
        self.fields['objectif'] = forms.CharField(
            label="Objectif",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Objectif', 'class': 'form-control'}),
            help_text='Objectif',
        )
        self.fields['realise'] = forms.CharField(
            label="Réalisé",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Réalisé', 'class': 'form-control'}),
            help_text='Réalisé',
        )
        self.fields['couleur'] = forms.ModelChoiceField(
            label="Couleur du scotch",
            queryset=Couleur.objects.all(),
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Couleur du scotch', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une couleur de scotch'
        )
        self.fields['rang'] = forms.CharField(
            label="N° du Rang",
            required=False,
            widget=forms.TextInput(attrs={'placeholder': 'N° du rang', 'class': 'form-control'}),
            help_text='Saisir un numéro de rang'
        )
        self.fields['reussi'] = forms.CharField(
            label="Reussi",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Reussi', 'class': 'form-control'}),
            help_text='Reussi',
        )
        self.fields['inventaire'] = forms.ModelChoiceField(
            label="Période",
            queryset=Inventaire.objects.all(),
            required=False,
            initial=inventaire_actif,
            widget=Select2Widget(attrs={'placeholder': 'Période', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une période',
        )

    class Meta:
        model = Greffons
        fields = ['produit', 'date', 'greffons', 'comm', 'objectif', 'realise', 'reussi', 'couleur', 'rang', 'inventaire']


class FormEditGreffon(forms.ModelForm):

    def __init__(self,  *args, **kwargs):
        self.produit = kwargs.pop('produit', None)
        self.greffons = kwargs.pop('greffons', None)
        self.comm = kwargs.pop('comm', None)
        self.objectif = kwargs.pop('objectif', None)
        self.realise = kwargs.pop('realise', None)
        self.reussi = kwargs.pop('reussi', None)
        self.date = kwargs.pop('date', None)
        self.couleur = kwargs.pop('couleur', None)
        self.rang = kwargs.pop('rang', None)
        self.inventaire = kwargs.pop('inventaire', None)
        super(FormEditGreffon, self).__init__(*args, **kwargs)

        inventaire_actif = Inventaire.objects.get(actif=True)

        self.fields['produit'] = forms.ModelChoiceField(
            label="Produits",
            queryset=Produit.objects.all(),
            required=False,
            disabled=True,
            widget=Select2Widget(attrs={'placeholder': 'Produit', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir un produit dans la liste des produit existant !')

        self.fields['date'] = forms.DateField(
            label="Date du greffon",
            required=False,
            initial=datetime.now(),
            widget=forms.DateInput(attrs={'placeholder': 'Date du greffon', 'class': 'datepicker_input form-control'}),
            help_text='Saisir une date à laquelle le greffon a été réalisé',
        )
        self.fields['greffons'] = forms.CharField(
            label="Nombre de greffons",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Nombre de greffons', 'class': 'form-control'}),
            help_text='Quantité de greffon',
        )
        self.fields['comm'] = forms.CharField(
            label="Quantité de produits pré-commandés",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Quantité de produits pré-commandés', 'class': 'form-control'}),
            help_text='Quantité de produits pré-commandés',
        )
        self.fields['objectif'] = forms.CharField(
            label="Objectif",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Objectif', 'class': 'form-control'}),
            help_text='Objectif',
        )
        self.fields['realise'] = forms.CharField(
            label="Réalisé",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Réalisé', 'class': 'form-control'}),
            help_text='Réalisé',
        )
        self.fields['couleur'] = forms.ModelChoiceField(
            label="Couleur du scotch",
            queryset=Couleur.objects.all(),
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Couleur du scotch', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une couleur de scotch'
        )
        self.fields['rang'] = forms.CharField(
            label="N° du Rang",
            required=False,
            widget=forms.TextInput(attrs={'placeholder': 'N° du rang', 'class': 'form-control'}),
            help_text='Saisir un numéro de rang'
        )
        self.fields['reussi'] = forms.CharField(
            label="Reussi",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Reussi', 'class': 'form-control'}),
            help_text='Reussi',
        )
        self.fields['inventaire'] = forms.ModelChoiceField(
            label="Période",
            queryset=Inventaire.objects.all(),
            required=False,
            initial=inventaire_actif,
            widget=Select2Widget(attrs={'placeholder': 'Période', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une période',
        )

    class Meta:
        model = Greffons
        fields = ['produit', 'date', 'greffons', 'comm', 'objectif', 'realise', 'reussi', 'couleur', 'rang', 'inventaire']


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

        self.fields['stock_bis'] = forms.IntegerField(
            label="Stock Virtuel (Commande en cours)",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Stock en cours du produit', 'class': 'form-control', 'value': 0}),
            help_text='Saisir une valeur pour le stock en cours... <br/>Valeur par défaut : Identique à celle du stock final')

        self.fields['stock_future'] = forms.IntegerField(
            label="Stock Future (Pré-commande)",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Stock futur du produit', 'class': 'form-control', 'value': 0}),
            help_text='Saisir une valeur pour le stock future... <br/>Valeur par défaut : 0')

        self.fields['prix'] = forms.IntegerField(
            label="Prix par défaut",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Prix par défaut', 'class': 'form-control', 'value': 0}),
            help_text='Saisir une valeur pour le prix par défaut... <br/>Valeur par défaut : 15')

        self.fields['gaf'] = forms.BooleanField(
            label="Greffe à façon",
            required=False,
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked': False}),
            help_text='Ce produit ne sera pas visible aux clients et ne servira qu\'une fois !')

    class Meta:
        model = Produit
        fields = ['nom', 'espece', 'variete', 'portegreffe', 'spec', 'stock', 'stock_bis', 'stock_future', 'prix', 'gaf']


# FORMULAIRE DEDIE A L'UPLOAD DU FICHIER EXCEL DE LA LISTE DES PRODUITS ------------------------------------------------------------------------
class ImportProduitForm(forms.ModelForm):

    class Meta:
        model = Produit
        fields = ['id', 'nom', 'slug', 'description', 'prix', 'stock',	'stock_bis', 'available', 'espece',	'variete', 'portegreffe', 'spec']


# FORMULAIRE DEDIE A L'AJOUT/EDITION D'UNE COULEUR
class FormCouleur(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.tva = kwargs.pop('tva', None)
        super(FormCouleur, self).__init__(*args, **kwargs)

        self.fields['nom'] = forms.CharField(
            label="Couleur de scotch",
            required=True,
            help_text='Indiquer un nom de couleur',
            widget=forms.TextInput(attrs={'placeholder': 'Saisir un nom de couleur', 'class': 'form-control'},)
        )

        self.fields['couleur'] = forms.CharField(
            label="Code couleur",
            required=True,
            help_text='Code couleur hexa #xxxxxx',
            widget=forms.TextInput(attrs={'placeholder': '#XXXXXX', 'class': 'form-control form-control-color', 'type': 'color'},)
        )

    class Meta:
        model = Couleur
        fields = ['nom', 'couleur']


class FormProduitList(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormProduitList, self).__init__(*args, **kwargs)

        dic = read_log(mode="produit")
        produit_id_list = []
        i = 0
        for p in dic['produit']:
            if p not in produit_id_list and dic['order'][i] is not None:
                produit_id_list.append(p)
            i += 1

        self.fields['nom'] = forms.ModelChoiceField(
            label="Produits",
            queryset=Produit.objects.filter(pk__in=produit_id_list),
            required=True,
            help_text='Choisir un produit')

    class Meta:
        model = Produit
        fields = ['nom']