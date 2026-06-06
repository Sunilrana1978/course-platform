from django.db import models
from django.conf import settings


class Plan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        app_label = 'subscriptions'

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    payment = models.ForeignKey('payments.Payment', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'subscriptions'
