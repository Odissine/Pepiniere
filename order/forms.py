from django import forms
from onlineshop.models import *
from .models import *
from django_select2.forms import Select2Widget, Select2MultipleWidget
from bootstrap_datepicker_plus.widgets import DatePickerInput
from decimal import Decimal


CLIENT_CHOICE = (
    ("1", "Tous"),
    ("2", "Actif"),
    ("3", "Inactif"),
)

class OrderAddProduitOrder(forms.Form):
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class SearchOrderForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.statut = kwargs.pop('statut', None)
        self.clients = kwargs.pop('clients', None)
        self.start_date = kwargs.pop('start_date', None)
        self.end_date = kwargs.pop('end_date', None)
        self.produits = kwargs.pop('produits', None)
        self.especes = kwargs.pop('especes', None)
        self.varietes = kwargs.pop('varietes', None)
        self.portegreffes = kwargs.pop('portegreffes', None)
        self.frais = kwargs.pop('frais', None)
        self.inventaire = kwargs.pop('inventaire', None)
        super(SearchOrderForm, self).__init__(*args, **kwargs)

        self.fields['statut'] = forms.ModelMultipleChoiceField(
            label="Statut",
            queryset=Statut.objects.all(),
            required=False,
            widget=Select2MultipleWidget(attrs={'placeholder': 'Statut', 'class': 'form-control js-example-basic-single'}),
            help_text='Séléctionner un statut')

        self.fields['clients'] = forms.ModelMultipleChoiceField(
            label="Clients",
            queryset=Client.objects.all(),
            required=False,
            widget=Select2MultipleWidget(attrs={'placeholder': 'Clients', 'class': 'form-control js-example-basic-single'}),
            help_text='Séléctionner un client')

        current_year = datetime.now().year
        previous_year = datetime.now().year - 1

        self.fields['start_date'] = forms.DateField(
            label="Commandes passées après",
            required=False,
            widget=forms.DateInput(attrs={'placeholder': 'Date début', 'class': 'datepicker_input form-control'}),
            help_text='Séléctionner une date après laquelle les commandes ont été passées',
            initial=datetime.strptime('%s-01-01' % previous_year, '%Y-%m-%d')
        )

        self.fields['end_date'] = forms.DateField(
            label="Commandes passées avant",
            required=False,
            widget=forms.DateInput(attrs={'placeholder':'Date fin', 'class': 'datepicker_input form-control'}),
            help_text='Séléctionner une date avant laquelle les commandes ont été passées',
            initial=datetime.strptime('%s-12-31' % current_year, '%Y-%m-%d')
        )

        self.fields['produits'] = forms.ModelMultipleChoiceField(
            label="Produits",
            queryset=Produit.objects.all(),
            required=False,
            widget=Select2MultipleWidget(attrs={'placeholder': 'Produits', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir un produit')

        self.fields['especes'] = forms.ModelMultipleChoiceField(
            label="Espèces",
            queryset=Espece.objects.all(),
            required=False,
            widget=Select2MultipleWidget(attrs={'placeholder': 'Especes', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une espèce')

        self.fields['varietes'] = forms.ModelMultipleChoiceField(
            label="Variétés",
            queryset=Variete.objects.all(),
            required=False,
            widget=Select2MultipleWidget(attrs={'placeholder': 'Variétés', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une variété')

        self.fields['portegreffes'] = forms.ModelMultipleChoiceField(
            label="Porte-Greffes",
            queryset=PorteGreffe.objects.all(),
            required=False,
            widget=Select2MultipleWidget(attrs={'placeholder': 'Porte-Greffes', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir un porte-greffe')

        self.fields['frais'] = forms.ModelMultipleChoiceField(
            label="Frais",
            queryset=Frais.objects.all(),
            required=False,
            widget=Select2MultipleWidget(attrs={'placeholder': 'Frais', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir un type de frais')

        self.fields['inventaire'] = forms.ModelMultipleChoiceField(
            label="Période",
            queryset=Inventaire.objects.all().order_by('-start_date'),
            required=False,
            widget=Select2MultipleWidget(attrs={'placeholder': 'Période', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une période')

    class Meta:
        model = Commande
        fields = ['statut', 'clients', 'start_date', 'end_date', 'produits', 'especes', 'varietes', 'portegreffes', 'frais', 'inventaire', ]
        widgets = {
            'start_date': DatePickerInput(),  # default date-format %m/%d/%Y will be used
            'end_date': DatePickerInput(format='%Y-%m-%d'),  # specify date-frmat
        }


class FormResetOrder(forms.Form):

    def __init__(self, *args, **kwargs):
        self.inventaire = kwargs.pop('inventaire', None)
        super(FormResetOrder, self).__init__(*args, **kwargs)

        self.fields['inventaire'] = forms.ModelChoiceField(
            label="Période",
            queryset=Inventaire.objects.exclude(actif=True).order_by('-start_date'),
            required=True,
            widget=Select2Widget(attrs={'placeholder': 'Période', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir une période',
            initial=Inventaire.objects.get(start_date__lte=datetime.now(), end_date__gte=datetime.now())
        )

        self.fields['mode'] = forms.ChoiceField(
            label="Contrôle des stocks ?",
            choices=[('CHECK', 'Avec contrôle'), ('FULL', 'Sans contrôle')],
            required=True,
            widget=Select2Widget(attrs={'placeholder': 'Contrôler les stocks ?', 'class': 'form-control js-example-basic-single'}),
            help_text='Contrôler les stocks avant traitement ?')

    class Meta:
        model = Commande
        fields = ['inventaire', 'mode']


class SearchClientForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.cp = kwargs.pop('statut', None)
        self.ville = kwargs.pop('clients', None)
        self.remise = kwargs.pop('start_date', None)
        super(SearchClientForm, self).__init__(*args, **kwargs)

        self.fields['nom'] = forms.CharField(
            label="Nom",
            required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Nom', 'class': 'form-control'}),
            help_text='Saisir le nom de famille ou une partie du nom du client'
        )

        self.fields['prenom'] = forms.CharField(
            label="Prénom",
            required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Prénom', 'class': 'form-control'}),
            help_text='Saisir le prénom (ou une partie)'
        )

        self.fields['cp'] = forms.CharField(
            label="Code Postal",
            required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Code Postal', 'class': 'form-control'}),
            help_text='Saisir un code postal'
        )

        self.fields['ville'] = forms.ChoiceField(
            label="Villes",
            choices=Client.objects.all().values_list('ville', 'ville').distinct(),
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Villes', 'class': 'form-control js-example-basic-single'}),
            help_text='Séléctionner une ville',
        )

        self.fields['remise'] = forms.DecimalField(
            label="Remise",
            required=False,
            widget=forms.NumberInput(attrs={'placeholder': 'Taux de remise', 'class': 'form-control'}),
            help_text='Saisir un taux de remise (sans le %)',
        )

        self.fields['activate'] = forms.ChoiceField(
            label="Statut",
            choices=CLIENT_CHOICE,
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Statut', 'class': 'form-control js-example-basic-single'}),
            help_text='Séléctionner un type de client.',
        )

        self.fields['mail'] = forms.CharField(
            label="Mail",
            required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Mail', 'class': 'form-control'}),
            help_text='Saisir une adresse mail'
        )

    class Meta:
        model = Client
        fields = ['cp', 'ville', 'remise', 'activate', 'mail']


class FormAddTva(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.tva = kwargs.pop('tva', None)
        super(FormAddTva, self).__init__(*args, **kwargs)

        self.fields['tva'] = forms.DecimalField(
            label="Taux de TVA",
            required=True,
            help_text='Indiquer le taux de la TVA (sans le %, ex: 5,5)',
            widget=forms.TextInput(attrs={'placeholder': 'Saisir un taux de TVA', 'class': 'form-control'},)
        )

        self.fields['default'] = forms.BooleanField(
            label="Taux par défaut",
            required=False,
            help_text='Taux par défaut pour toute les commande ?',
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked': False})
        )

        self.fields['active'] = forms.BooleanField(
            label="Taux actif",
            required=False,
            help_text='Taux actif pour les futures commandes ?',
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked': False})
        )

    class Meta:
        model = Tva
        fields = ['tva', 'default', 'active']


class FormAddStatut(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.nom = kwargs.pop('nom', None)
        super(FormAddStatut, self).__init__(*args, **kwargs)

        self.fields['nom'] = forms.CharField(
            label="Nom du statut",
            required=True,
            help_text="Indiquer un nom pour le statut",
            widget=forms.TextInput(attrs={'placeholder': 'Saisir le nom du Statut', 'class': 'form-control'}),
        )

    class Meta:
        model = Statut
        fields = ['nom']


class FormAddFrais(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.nom = kwargs.pop('nom', None)
        self.tva = kwargs.pop('tva', None)
        super(FormAddFrais, self).__init__(*args, **kwargs)

        self.fields['nom'] = forms.CharField(
            label="Nom du frais",
            required=True,
            help_text='Indiquer un nom associé au frais (transport, ...)',
            widget=forms.TextInput(attrs={'placeholder': 'Saisir un nom pour le type de Frais', 'class': 'form-control'})
        )

        self.fields['tva'] = forms.ModelChoiceField(
            label="TVA",
            queryset=Tva.objects.all(),
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Taux de TVA associé au frais', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir un taux de TVA')

    class Meta:
        model = Frais
        fields = ['nom', 'tva']


class FormInventaire(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.start_date = kwargs.pop('nom', None)
        self.end_date = kwargs.pop('tva', None)
        super(FormInventaire, self).__init__(*args, **kwargs)

        self.fields['start_date'] = forms.DateField(
            label="Debut des commandes",
            required=True,
            widget=forms.DateInput(attrs={'placeholder': 'Date début', 'class': 'datepicker_input form-control'}),
            help_text='Séléctionner la date de reprsie des commandes'
        )

        self.fields['end_date'] = forms.DateField(
            label="Fin des commandes",
            required=True,
            widget=forms.DateInput(attrs={'placeholder': 'Date fin', 'class': 'datepicker_input form-control'}),
            help_text='Séléctionner la date de cloture des commandes (stock remis a zero ...)'
        )

    def clean(self):
        data = self.cleaned_data
        if data.get('end_date', None) and data.get('start_date', None):
            if data.get('start_date') > data.get('end_date'):
                raise forms.ValidationError('La date de début doit etre inférieur à la date de fin !')

    class Meta:
        model = Inventaire
        fields = ['start_date', 'end_date']


class FormAddClient(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.prenom = kwargs.pop('tva', None)
        self.nom = kwargs.pop('tva', None)
        self.societe = kwargs.pop('tva', None)
        self.cp = kwargs.pop('tva', None)
        self.ville = kwargs.pop('tva', None)
        self.adresse = kwargs.pop('tva', None)
        self.tel = kwargs.pop('tva', None)
        self.mail = kwargs.pop('tva', None)
        self.commentaire = kwargs.pop('tva', None)
        self.remise = kwargs.pop('tva', None)
        super(FormAddClient, self).__init__(*args, **kwargs)

        self.fields['prenom'] = forms.CharField(
            label="Prénom",
            required=False,
            help_text='Saisir le prénom',
            widget=forms.TextInput(attrs={'placeholder': 'Saisir le prénom', 'class': 'form-control'},)
        )

        self.fields['nom'] = forms.CharField(
            label="Nom",
            required=False,
            help_text='Saisir le nom',
            widget=forms.TextInput(attrs={'placeholder': 'Saisir le nom', 'class': 'form-control'}, )
        )

        self.fields['societe'] = forms.CharField(
            label="Societe",
            required=False,
            help_text='Saisir le nom de la société',
            widget=forms.TextInput(attrs={'placeholder': 'Saisir le nom de la société', 'class': 'form-control'}, )
        )

        self.fields['adresse'] = forms.CharField(
            label="Adresse",
            required=False,
            help_text='Saisir une adresse',
            widget=forms.Textarea(attrs={'placeholder': 'Saisir une adresse', 'class': 'form-control', 'rows': 2})
        )

        self.fields['cp'] = forms.CharField(
            label="Code Postal",
            required=False,
            help_text='Saisir le code postal',
            widget=forms.NumberInput(attrs={'placeholder': 'Saisir le code postal', 'class': 'form-control'}, )
        )

        self.fields['ville'] = forms.CharField(
            label="Ville",
            required=False,
            help_text='Saisir la ville',
            widget=forms.TextInput(attrs={'placeholder': 'Saisir la ville', 'class': 'form-control'}, )
        )

        self.fields['tel'] = forms.CharField(
            label="Tel",
            required=False,
            help_text='Saisir le numéro de téléphone',
            widget=forms.NumberInput(attrs={'placeholder': 'Saisir le numéro de téléphone', 'class': 'form-control'}, )
        )

        self.fields['mail'] = forms.EmailField(
            label="Email",
            required=False,
            help_text='Saisir l\'adresse mail',
            widget=forms.EmailInput(attrs={'placeholder': 'Saisir l\'adresse mail', 'class': 'form-control'}, )
        )

        self.fields['commentaire'] = forms.CharField(
            label="Commentaire",
            required=False,
            help_text='Saisir un commentaire',
            widget=forms.Textarea(attrs={'placeholder': 'Saisir un commentaire', 'class': 'form-control', 'rows': 2})
        )

        self.fields['remise'] = forms.DecimalField(
            label="Remise",
            required=False,
            initial=Decimal('0.00'),
            help_text='Saisir un taux de remise',
            widget=forms.NumberInput(attrs={'placeholder': 'Saisir un taux de remise', 'class': 'form-control'}, )
        )

        self.fields['user'] = forms.ModelChoiceField(
            label="Utilisateur",
            queryset=User.objects.all(),
            required=False,
            widget=Select2Widget(attrs={'placeholder': 'Utilisateur', 'class': 'form-control js-example-basic-single'}),
            help_text='Choisir un utilisateur du site'
        )

    class Meta:
        model = Client
        fields = ['prenom', 'nom', 'societe', 'adresse', 'cp', 'ville', 'tel', 'mail', 'remise', 'commentaire', 'user']


class FormAddOrder(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.client = kwargs.pop('tva', None)
        self.remise = kwargs.pop('tva', None)
        self.statut = kwargs.pop('tva', None)
        self.tva = kwargs.pop('tva', None)
        self.frais = kwargs.pop('tva', None)
        self.montant_frais = kwargs.pop('tva', None)
        self.date = kwargs.pop('tva', None)
        super(FormAddOrder, self).__init__(*args, **kwargs)

        self.fields['client'] = forms.ModelChoiceField(
            label="Client",
            queryset=Client.objects.all().order_by('prenom', 'nom'),
            required=True,
            help_text='Choisir un client',
            widget=Select2Widget(attrs={'placeholder': 'Choisir un client', 'class': 'form-control js-example-basic-single'},)
        )

        self.fields['remise'] = forms.DecimalField(
            label="Remise",
            required=True,
            help_text='Saisir une remise',
            widget=forms.NumberInput(attrs={'placeholder': 'Saisir une remise', 'class': 'form-control'}, )
        )

        self.fields['statut'] = forms.ModelChoiceField(
            label="Statut",
            required=True,
            queryset=Statut.objects.all(),
            help_text='Choisir un statut',
            widget=Select2Widget(attrs={'placeholder': 'Choisir un statut', 'class': 'form-control js-example-basic-single'})
        )

        self.fields['tva'] = forms.ModelChoiceField(
            label="TVA",
            required=True,
            queryset=Tva.objects.all(),
            help_text='Choisir un taux de TVA',
            widget=Select2Widget(attrs={'placeholder': 'Choisir un taux de TVA', 'class': 'form-control js-example-basic-single'})
        )

        self.fields['frais'] = forms.ModelChoiceField(
            label="Frais",
            required=False,
            queryset=Frais.objects.all(),
            help_text='Choisir un type de frais',
            widget=Select2Widget(attrs={'placeholder': 'Choisir un type de frais', 'class': 'form-control js-example-basic-single'})
        )

        self.fields['montant_frais'] = forms.DecimalField(
            label="Montant des frais",
            required=False,
            help_text='Saisir un montant pour les frais',
            widget=forms.NumberInput(attrs={'placeholder': 'Saisir un montant pour les frais', 'class': 'form-control'})
        )

        self.fields['date'] = forms.DateTimeField(
            label="Date de création",
            required=True,
            widget=forms.DateInput(attrs={'placeholder': 'Date de création', 'class': 'datepicker_input form-control'}),
            help_text='Séléctionner une date pour la création de la commande',
        )

        self.fields['inventaire'] = forms.ModelChoiceField(
            label="Période",
            required=True,
            queryset=Inventaire.objects.all(),
            help_text='Choisir une période',
            widget=Select2Widget(attrs={'placeholder': 'Choisir une période', 'class': 'form-control js-example-basic-single'})
        )

    class Meta:
        model = Commande
        fields = ['client', 'remise', 'statut', 'date', 'tva', 'frais', 'montant_frais', 'inventaire']


class FormAddProduit(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.produit = kwargs.pop('produit', None)
        self.prix = kwargs.pop('prix', None)
        self.qte = kwargs.pop('qte', None)
        self.order = kwargs.pop('order', None)
        super(FormAddProduit, self).__init__(*args, **kwargs)

        if self.order.statut.nom == "Pré-commande":
            queryset_produit = Produit.objects.all()
        else:
            queryset_produit = Produit.objects.filter(stock_bis__gt=0)

        self.fields['produit'] = forms.ModelChoiceField(
            label="Produit",
            required=False,
            queryset=queryset_produit,
            help_text='Choisir un produit',
            widget=Select2Widget(attrs={'placeholder': 'Choisir un produit', 'class': 'form-control js-example-basic-single addproduct_modal'})
        )

        self.fields['prix'] = forms.DecimalField(
            label="Prix",
            required=False,
            help_text='Saisir un prix',
            widget=forms.NumberInput(attrs={'placeholder': 'Saisir un prix', 'class': 'form-control', 'value': 15})
        )

        self.fields['qte'] = forms.IntegerField(
            label="Quantité",
            required=True,
            help_text='Saisir une quantité',
            widget=forms.NumberInput(attrs={'placeholder': 'Saisir une quantité', 'class': 'form-control', 'default': 1, 'value': 1})
        )

    class Meta:
        model = Cartdb
        fields = ['produit', 'prix', 'qte']


class FormEditProduit(forms.ModelForm):

    def __init__(self, produit_id,  *args, **kwargs):
        self.produit = kwargs.pop('produit', None)
        self.prix = kwargs.pop('prix', None)
        self.qte = kwargs.pop('qte', None)
        super(FormEditProduit, self).__init__(*args, **kwargs)

        self.fields['produit'] = forms.ModelChoiceField(
            label="Produit",
            required=False,
            disabled=True,
            queryset=Produit.objects.filter(id=produit_id),
            help_text='Choisir un produit',
            widget=Select2Widget(attrs={'placeholder': 'Choisir un produit', 'class': 'form-control js-example-basic-single'})
        )

        self.fields['prix'] = forms.DecimalField(
            label="Prix",
            required=False,
            help_text='Saisir un prix',
            widget=forms.NumberInput(attrs={'placeholder': 'Saisir un prix', 'class': 'form-control', 'value': 15})
        )

        self.fields['qte'] = forms.IntegerField(
            label="Quantité",
            required=True,
            help_text='Saisir une quantité',
            widget=forms.NumberInput(attrs={'placeholder': 'Saisir une quantité', 'class': 'form-control', 'default': 1})
        )

    class Meta:
        model = Cartdb
        fields = ['produit', 'prix', 'qte']