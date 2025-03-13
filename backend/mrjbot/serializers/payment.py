from rest_framework import serializers

from .base import BaseModelSerializer
from ..models import Payment, Transaction, Commission, WithdrawalRequest


class PaymentSerializer(BaseModelSerializer):
    """Serializer for Payment model."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    subscription_plan = serializers.CharField(source='subscription.plan.name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_username', 'subscription',
            'subscription_plan', 'amount', 'status',
            'payment_method', 'transaction_id', 'payment_data',
            'notes', 'created_at', 'updated_at', 'is_active',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new payment."""
    class Meta:
        model = Payment
        fields = ['user', 'subscription', 'amount', 'payment_method', 'notes']


class TransactionSerializer(BaseModelSerializer):
    """Serializer for Transaction model."""
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'user_username', 'type',
            'amount', 'status', 'reference',
            'description', 'created_at', 'updated_at',
            'is_active',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']


class CommissionSerializer(BaseModelSerializer):
    """Serializer for Commission model."""
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    subscription_plan = serializers.CharField(source='subscription.plan.name', read_only=True)

    class Meta:
        model = Commission
        fields = [
            'id', 'seller', 'seller_username', 'subscription',
            'subscription_plan', 'amount', 'status',
            'transaction', 'notes', 'created_at',
            'updated_at', 'is_active',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']


class WithdrawalRequestSerializer(BaseModelSerializer):
    """Serializer for WithdrawalRequest model."""
    seller_username = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        model = WithdrawalRequest
        fields = [
            'id', 'seller', 'seller_username', 'amount',
            'status', 'transaction', 'bank_account',
            'notes', 'created_at', 'updated_at',
            'is_active',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']


class WithdrawalRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new withdrawal request."""
    class Meta:
        model = WithdrawalRequest
        fields = ['amount', 'bank_account', 'notes']

    def validate(self, attrs):
        seller = self.context['request'].user
        amount = attrs['amount']

        # Check if seller has enough balance
        if seller.balance < amount:
            raise serializers.ValidationError(
                "Insufficient balance for withdrawal."
            )

        # Check if seller has any pending withdrawal requests
        if WithdrawalRequest.objects.filter(
            seller=seller,
            status='pending',
            is_active=True
        ).exists():
            raise serializers.ValidationError(
                "You already have a pending withdrawal request."
            )

        return attrs 