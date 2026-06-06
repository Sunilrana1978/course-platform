from rest_framework import serializers
from .models import Plan, UserSubscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ('id', 'name', 'price', 'duration_days', 'description')


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_detail = PlanSerializer(source='plan', read_only=True)
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = ('id', 'plan', 'plan_detail', 'start_date', 'end_date', 'is_active', 'days_remaining')

    def get_days_remaining(self, obj):
        from django.utils import timezone
        if not obj.is_active:
            return 0
        remaining = (obj.end_date - timezone.now()).days
        return max(0, remaining)
