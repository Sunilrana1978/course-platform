from rest_framework import serializers
from apps.courses.serializers import CourseSerializer
from apps.subscriptions.serializers import PlanSerializer
from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    course_detail = CourseSerializer(source='course', read_only=True)
    plan_detail = PlanSerializer(source='plan', read_only=True)
    price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'item_type', 'course', 'plan', 'course_detail', 'plan_detail', 'price', 'added_at')
        read_only_fields = ('added_at',)

    def validate(self, data):
        item_type = data.get('item_type')
        if item_type == CartItem.ITEM_TYPE_COURSE and not data.get('course'):
            raise serializers.ValidationError('course is required for item_type=course')
        if item_type == CartItem.ITEM_TYPE_PLAN and not data.get('plan'):
            raise serializers.ValidationError('plan is required for item_type=plan')
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
