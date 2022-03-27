from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django_select2.forms import Select2Widget, ModelSelect2Widget, Select2MultipleWidget
from django.forms import ModelMultipleChoiceField, ModelChoiceField
from .models import *

class UsernameChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s %s" % (obj.first_name, obj.last_name)


class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        required=False,
        error_messages={'required': 'Merci de saisir un nom d\'utilisateur'},
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'placeholder': 'Nom d\'utilisateur', 'autocomplete': 'off', 'class': 'form-control'}),
        help_text="Si vous laissez le champ vide, pour vous connecter il vous faudra saisir votre adresse mail.",

    )

    first_name = forms.CharField(
        required=True,
        error_messages={'required': 'Merci de saisir votre prénom'},
        label='Prénom',
        widget=forms.TextInput(attrs={'placeholder': 'Prénom', 'autocomplete': 'off', 'class': 'form-control', 'required': 'required'})
    )

    last_name = forms.CharField(
        required=True,
        error_messages={'required': 'Merci de saisir votre nom de famille'},
        label='Nom',
        widget=forms.TextInput(attrs={'placeholder': 'Nom', 'autocomplete': 'off', 'class': 'form-control', })
    )

    email = forms.EmailField(
        required=True,
        error_messages={'required': 'Merci de saisir une adresse mail valide'},
        label='Email',
        widget=forms.TextInput(attrs={'placeholder': 'Email', 'autocomplete': 'off', 'class': 'form-control', })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
        label='Mot de passe'
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmation du mot de passe'}),
        label='Confirmation du mot de passe'
    )

    def clean(self):
        error = {}
        cleaned_data = super().clean()
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        pass1 = self.cleaned_data['password']
        pass2 = self.cleaned_data['password2']
        if pass1 != pass2:
            error['password'] = "Les mots de passe ne correspondent pas"
            # raise forms.ValidationError("Les mots de passe ne correspondent pas")

        username_exist = User.objects.filter(username=username)
        if len(username_exist) > 0:
            error['username'] = "Le nom d'utilisateur existe déjà !"
            # raise forms.ValidationError("Le nom d'utilisateur existe déjà !")

        email_exist = User.objects.filter(email=email)
        if len(email_exist) > 0:
            error['email'] = "L'adresse mail existe déjà !"
            # raise forms.ValidationError("L'adresse mail existe déjà !")
        if error:
            raise forms.ValidationError(error)

    def save(self, commit=True):
        instance = super(RegisterForm, self).save(commit=False)
        username = self.cleaned_data['username']
        if username is None or username == "":
            instance.username = self.cleaned_data['email']
        instance.email = self.cleaned_data['email']
        if commit:
            instance.save()

        return instance

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'password2')


class UserLoginForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur", 'autofocus': 'None'}), label="", required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe', 'autocomplete': 'off'}), label='Mot de passe')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Désolé, cet identifiant n'existe pas ! Essaye encore ... ou créé toi un compte :)")
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['username', 'password']


class FormResetPassword(forms.Form):
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
        label='Mot de passe'
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmation du mot de passe'}),
        label='Confirmation du mot de passe'
    )

    class Meta:
        fields = ['password2', 'password']


'''
class FormConfig(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.register = kwargs.pop('register', None)
        super(FormConfig, self).__init__(*args, **kwargs)

    try:
        config = Config.objects.get(id=1)
    except:
        config = Config.objects.create(register=False)
        config.save()

    register = forms.ChoiceField(
        required=True,
        choices=[('True', 'Oui'), ('False', 'Non')],
        label='Création de compte ?',
        initial=config.register,
        widget=Select2Widget(attrs={'placeholder': 'Création de compte ?', 'class': 'form-control js-example-basic-single'}),
    )

    class Meta:
        model = Config
        fields = ['register']
'''