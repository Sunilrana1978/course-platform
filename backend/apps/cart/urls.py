from django.urls import path
from .views import cart_detail, add_item, remove_item, clear_cart

urlpatterns = [
    path('', cart_detail, name='cart'),
    path('items/', add_item, name='cart-add'),
    path('items/<int:pk>/', remove_item, name='cart-remove'),
    path('clear/', clear_cart, name='cart-clear'),
]
