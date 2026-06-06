from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'amount', 'currency', 'status', 'gateway', 'gateway_ref',
                  'error_detail', 'created_at', 'updated_at')


class InitiatePaymentSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(max_length=128)
    cart_items = serializers.ListField(child=serializers.DictField())


class ConfirmPaymentSerializer(serializers.Serializer):
    payment_id = serializers.UUIDField()
    card_number = serializers.CharField(max_length=19)
    card_expiry = serializers.CharField(max_length=7)
    card_cvc = serializers.CharField(max_length=4)
    card_name = serializers.CharField(max_length=100)
