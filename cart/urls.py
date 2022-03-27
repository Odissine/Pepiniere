from django.urls import path
from . import views


app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart-detail'),
    path('valid/', views.cart_valid, name='cart-valid'),
    path('cancel/', views.cart_cancel, name='cart-cancel'),
    path('add/<produit_id>', views.cart_add, name='cart-add'),
    path('add_ajax/<produit_id>', views.cart_add_ajax, name='cart-add-ajax'),
    path('update/<produit_id>', views.cart_update, name='cart-update'),
    path('remove/<produit_id>', views.cart_remove, name='cart-remove'),
]
