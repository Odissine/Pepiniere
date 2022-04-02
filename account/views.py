from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.html import format_html
from django.contrib.auth.decorators import login_required

from .core import *
from .forms import *
from .models import *
from order.forms import FormAddClient
from order.models import Client
from pepiniere.settings import DEBUG


def home(request):
    return render(request, 'onlineshop/list.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        if check_mail_or_username(username):
            try:
                username = User.objects.get(email=username.lower()).username
            except:
                messages.error(request, "Cet email n'existe pas dans la base !")
                return render(request, "account/login.html")
        else:
            try:
                username = User.objects.get(username__iexact=username)
            except:
                messages.error(request, "Ce nom d'utilisateur n'existe pas dans la base !")
                return render(request, "account/login.html")
        print(username)
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect("onlineshop:produit-list")
        else:
            messages.error(request, "Erreur d'authentification ! Merci de réessayer.")

    return render(request, "account/login.html")


def logout_view(request):
    logout(request)
    return redirect("/account/login/")


def register(request):
    if allow_register() is False:
        messages.error(request, "La création de compte est désactivée !")
        return redirect('produit-list')

    user_form = RegisterForm(request.POST or None)
    client_form = FormAddClient(request.POST or None)

    if request.method == "POST":
        if user_form.is_valid() and client_form.is_valid():
            user_form.save()
            email = user_form.cleaned_data['email']
            password = user_form.cleaned_data['password']
            last_user = User.objects.get(email=email)
            last_user.set_password(password)
            last_user.save()

            check_mail_client = Client.objects.filter(mail=email)
            if len(check_mail_client) > 0:
                last_client = Client.objects.get(mail=email)
                last_client.user = last_user
            else:
                client_form.save()
                last_client = Client.objects.last()
                last_client.user = last_user
                last_client.prenom = last_user.first_name
                last_client.nom = last_user.last_name
                last_client.mail = last_user.email
            last_client.save()
            messages.success(request, "Compte créé avec succès.")
            return redirect('account:login')
        else:
            messages.error(request, "Une erreur s'est produite ... Merci de réessayer !.")
    context = {
        'user_form': user_form,
        'client_form': client_form,
    }
    return render(request, "account/register.html", context)


@login_required
def user_profil(request):
    user = request.user
    client = Client.objects.get(user=user)
    user_form = RegisterModifyForm(request.POST or None, instance=user)
    client_form = FormAddClient(request.POST or None, instance=client)

    if request.POST:
        if request.POST.get('mode') == "profil":
            if user_form.is_valid() and client_form.is_valid():
                user_form.save()
                email = user_form.cleaned_data['email']
                last_user = User.objects.get(email=email)
                last_user.save()
                try:
                    client = Client.objects.get(user=last_user)
                    client.adresse = client_form.cleaned_data['adresse']
                    client.ville = client_form.cleaned_data['ville']
                    client.cp = client_form.cleaned_data['cp']
                    client.tel = client_form.cleaned_data['tel']
                    client.societe = client_form.cleaned_data['societe']
                    client.mail = email
                    client_form.save()
                except:
                    try:
                        client = Client.objects.get(email=email)
                        client.user = last_user
                    except:
                        client_form.save()
                        client = Client.objects.get(email=email)
                        client.user = last_user


                client.prenom = last_user.first_name
                client.nom = last_user.last_name

                client.save()
                messages.success(request, "Profil modifié avec succès.")
                return redirect('account:profil')
        elif request.POST.get('mode') == 'password':
            if user.check_password(request.POST.get('old-pass')):
                print("Go")

        else:
            messages.error(request, "Action interdite !.")
            return redirect('account:profil')
    context = {
        'user_form': user_form,
        'client_form': client_form,
        'client': client,
    }
    return render(request, "account/modify.html", context)


def error_view(request):
    context = {}
    return render(request, "account/error.html", context)


def change_password(request, user, token):
    try:
        user = User.objects.get(id=user)
    except:
        messages.error(request, "Vous n'êtes pas autorisé à modifier le mot de passe.")
        return redirect("account:login")

    try:
        token = TokenLogin.objects.get(user=user, token=token)
    except:
        messages.error(request, "Vous n'êtes pas autorisé à modifier le mot de passe.")
        return redirect("account:login")

    if request.POST:
        if request.POST.get('pass1') == request.POST.get('pass2') and request.POST.get('pass1') != "":
            user = request.POST.get('user')
            try:
                user = User.objects.get(id=user)
            except:
                messages.error(request, "Vous n'êtes pas autorisé à modifier le mot de passe.")
                return redirect("account:login")

            user.set_password(request.POST.get('pass1'))
            user.save()
            token.delete()

            if DEBUG is True:
                href = "http://127.0.0.1:8000/account/login"
            else:
                href = "https://stock.lapetitepepiniere.fr/account/login"

            email_html = "<br/><br/>Bonjour " + user.first_name + ",<br/><br/>"
            email_html += "Vous venez de modifier votre mot de passe pour accéder au site <a href='http://lapetitepepiniere.fr'>La Petite Pépinière</a><br>"
            email_html += "Cliquez sur le lien ci-dessous afin de pouvoir vous identifier.<br/><br/>"
            email_html += "<a href='" + href + "'>Identification</a><br/><br/>"
            email_html += "Si vous n'êtes pas à l'origine de cette demande, veuillez nous contacter afin que l'on puisse vous réinitialiser votre mot de passe.<br/><br/>"
            email_html += "La petite pepinière"
            send_mail("La petite pépinière - Nouveau mot de passe", email_html, '', '', [user.email], [])

            messages.success(request, format_html("Votre mot de passe a bien été réinitialisé."))
            return redirect("account:login")
        else:
            messages.error(request, format_html("Les mots de passe ne correspondent pas !<br> Veuillez réessayer."))
            return redirect('account:reset', user.id, token.token)

    form = FormResetPassword(request.POST or None)
    context = {
        'form': form,
        'user': user,
        'token': token.token,
    }
    return render(request, "account/reset.html", context)


def lost_password(request):
    if request.method == "POST":
        username = request.POST['username']
        if check_mail_or_username(username):
            try:
                user = User.objects.get(email=username.lower()).username
            except:
                messages.error(request, "Cet email n'existe pas dans la base !")
                return render(request, "account/forget.html")
        else:
            try:
                user = User.objects.get(username__iexact=username)
            except:
                messages.error(request, "Ce nom d'utilisateur n'existe pas dans la base !")
                return render(request, "account/forget.html")

        token_mail = generate_random_token(40)
        create_token = TokenLogin.objects.create(token=token_mail, user=user)

        if DEBUG is True:
            href = "http://127.0.0.1:8000/account/reset/" + str(user.id) + "/" + str(token_mail)
        else:
            href = "https://stock.lapetitepepiniere.fr/account/reset/" + str(user.id) + "/" + str(token_mail)

        email_html = "<br/><br/>Bonjour " + user.first_name + ",<br/><br/>"
        email_html += "Vous venez de faire une demande de réinitialisation de mot de passe sur le site <a href='http://lapetitepepiniere.fr'>La Petite Pépinière</a><br>"
        email_html += "Cliquez sur le lien ci-dessous afin de pouvoir changer votre mot de passe <br/><br/>"
        email_html += "<a href='" + href + "'>Changer son mot de passe</a><br/><br/>"
        email_html += "Si vous n'êtes pas à l'origine de cette demande, veuillez ne pas tenir compte de ce mail.<br/><br/>"
        email_html += "La petite pepinière"
        send_mail("La petite pépinière - Mot de passe oublié", email_html, '', '', [user.email], [])

        messages.success(request, "Un email vient de vous être envoyé !")
        return redirect("account:login")
        # user = authenticate(request, username=username, password=password)

    context = {}
    return render(request, "account/forget.html", context)


def change_config(request):
    form = FormConfig(request.POST or None)
    try:
        config = Config.objects.get(id=1)
    except:
        config = Config.objects.create(register=False)
        config.save()

    if request.POST:
        if form.is_valid():
            config.register = form.cleaned_data['register']
            config.save()
            messages.success(request, "Change de configuration enregistrée !")
            return redirect('produit-list')

    context = {
        'form': form,
        'config': config,
    }
    return render(request, "account/config.html", context)
