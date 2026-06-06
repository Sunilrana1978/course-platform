from django.urls import path
from .views import initiate, confirm, payment_status

urlpatterns = [
    path('initiate/', initiate, name='payment-initiate'),
    path('confirm/', confirm, name='payment-confirm'),
    path('<uuid:pk>/status/', payment_status, name='payment-status'),
]
