from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls import url
from . import views

app_name = 'account'

urlpatterns = [
    url(r'^login/$', view=LoginView.as_view(template_name="account/login.html", redirect_authenticated_user=True), name="login"),
    url(r'^logout/$', view=LogoutView.as_view(), name="logout")
]
