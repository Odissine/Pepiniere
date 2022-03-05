from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django_select2.forms import Select2Widget, ModelSelect2Widget, Select2MultipleWidget
from django.forms import ModelMultipleChoiceField, ModelChoiceField


class UsernameChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s %s" % (obj.first_name, obj.last_name)


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True, error_messages={'required': 'Merci de saisir votre prénom'}, label='', widget=forms.TextInput(attrs={'placeholder': 'Prénom', 'autocomplete': 'off'}))
    last_name = forms.CharField(required=True, error_messages={'required': 'Merci de saisir votre nom de famille'}, label='', widget=forms.TextInput(attrs={'placeholder': 'Nom', 'autocomplete': 'off'}))
    email = forms.EmailField(required=True, error_messages={'required': 'Merci de saisir une adresse mail valide'}, label='', widget=forms.TextInput(attrs={'placeholder': 'Email', 'autocomplete': 'off'}))
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label='', required=True, error_messages={'required': 'Merci de choisir votre classe'}, empty_label='Classe', widget=Select2Widget(attrs={'placeholder': "Classe", 'class': 'js-example-basic-single form-control select'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}), label='')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmation du mot de passe'}), label='')

    def save(self, commit=True):
        instance = super(RegisterForm, self).save(commit=False)
        instance.username = self.cleaned_data['email']
        instance.email = self.cleaned_data['email']
        if commit:
            instance.save()

        return instance

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'group', 'password1', 'password2')


class UserLoginForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur", 'autofocus': 'None'}), label="", required=True)
    # username = forms.ModelChoiceField(widget=Select2Widget(attrs={'placeholder': "Nom d'utilisateur", 'class': 'form-control'}), queryset=User.objects.all(), label="Nom d'utilisateur", required=True, help_text="Merci d'indiquer votre nom d'utilisateur")
    # username = UsernameChoiceField(label="Utilisateur", queryset=User.objects.all(), widget=Select2Widget(attrs={'placeholder': "Nom d'utilisateur", 'class': 'js-example-basic-single form-control select'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe', 'autocomplete': 'off'}), label='Mot de passe')
    # username.widget.attrs.update({"autofocus": False})

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
