from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls import url
from . import views
from .views import login_view, logout_view, register, error_view, lost_password, change_password, change_config


app_name = 'account'

urlpatterns = [
    # path('login/', views.login_view, name='login_view'),
    # path('logout/', views.logout_view, name='logout_view'),
    # path('login/success', views.login_success, name='login_success'),
    # path('logout/success', views.logout_success, name='logout_success'),
    # url(r'^login/$', view=LoginView.as_view(template_name="account/login.html", redirect_authenticated_user=True), name="login"),
    # url(r'^logout/$', view=LogoutView.as_view(template_name="account/login.html", next_page=None), name="logout")
    # path('login/', LoginView.as_view(template_name='account/login.html', redirect_authenticated_user=True), name="login"),
    # path('logout/', LogoutView.as_view(), name="logout"),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('forget/', lost_password, name='forget'),
    path('reset/<user>/<token>', change_password, name='reset'),
    path('error/', error_view, name='error'),
    path('config/', change_config, name='config'),
]
