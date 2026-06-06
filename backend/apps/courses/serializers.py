from rest_framework import serializers
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    has_access = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'price', 'category', 'category_display',
                  'thumbnail_url', 'duration_hours', 'instructor', 'has_access')

    def get_has_access(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        # Check direct course access
        if obj.accesses.filter(user=request.user).exists():
            return True
        # Check active subscription
        from apps.subscriptions.models import UserSubscription
        from django.utils import timezone
        return UserSubscription.objects.filter(
            user=request.user,
            is_active=True,
            end_date__gt=timezone.now()
        ).exists()
