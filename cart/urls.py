from django.urls import path
from . import views


app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('valid/', views.cart_valid, name='cart_valid'),
    path('cancel/', views.cart_cancel, name='cart_cancel'),
    # path('add/<int:produit_id>', views.cart_add, name='cart_add'),
    path('add/<int:produit_id>', views.cart_add_ajax, name='cart_add'),
    path('update/<int:produit_id>', views.cart_update, name='cart_update'),
    path('remove/<int:produit_id>', views.cart_remove, name='cart_remove'),
]
