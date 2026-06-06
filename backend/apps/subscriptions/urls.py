from django.urls import path
from .views import plan_list, my_subscription

urlpatterns = [
    path('plans/', plan_list, name='plan-list'),
    path('me/', my_subscription, name='my-subscription'),
]
