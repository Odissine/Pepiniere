from django.urls import path
from . import views


app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart-detail'),
    path('valid/', views.cart_valid, name='cart-valid'),
    path('prevalid/', views.pre_cart_valid, name='pre-cart-valid'),
    path('cancel/', views.cart_cancel, name='cart-cancel'),
    path('add/<int:produit_id>', views.cart_add, name='cart-add'),
    path('add_ajax/<int:produit_id>', views.cart_add_ajax, name='cart-add-ajax'),
    path('update/<int:produit_id>', views.cart_update, name='cart-update'),
    path('remove/<int:produit_id>', views.cart_remove, name='cart-remove'),
]
