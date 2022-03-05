from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def home(request):
    return render(request, 'onlineshop/list.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # print(user.groups.all())
            return redirect("onlineshop:produit-list")
        else:
            messages.error(request, "Erreur d'authentification ! Merci de réessayer.")

    return render(request, "account/login.html")


def logout_view(request):
    logout(request)
    return redirect("/account/login/")
    # return render(request, "account/login.html")
#
#
# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#
#         if user is not None:
#             login(request,user)
#             return redirect('/onlineshop/list.html')
#         else:
#             message = "Erreur d'identification !"
#             messages.success(request, message)
#             return redirect('account:login_view')
#     else:
#         return render(request, 'account/login.html')
#
#
# def logout_view(request):
#     logout(request)
#     return redirect('account/logout_success.html')
#
#
# def login_success(request):
#     return render(request, 'onlineshop/list.html')
#
#
# def logout_success(request):
#     return redirect('account/logout_success.html')
