from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from main.models import Server, SubscriptionPlan, Subscription
from v2ray.models import Inbound, Client, SyncLog, ClientConfig
from payments.models import Transaction, CardPayment, ZarinpalPayment, PaymentMethod, Discount
from telegrambot.models import TelegramMessage, TelegramNotification

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'telegram_id', 'phone_number', 
                  'language_code', 'is_admin', 'wallet_balance', 'date_joined', 
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'date_joined', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class ServerSerializer(serializers.ModelSerializer):
    """Serializer for the Server model"""
    
    class Meta:
        model = Server
        fields = ['id', 'name', 'url', 'username', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'session_cookie': {'write_only': True},
            'session_expiry': {'write_only': True}
        }


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for the SubscriptionPlan model"""
    
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'description', 'type', 'data_limit_gb', 
                  'duration_days', 'price', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for the Subscription model"""
    user = UserSerializer(read_only=True)
    plan = SubscriptionPlanSerializer(read_only=True)
    server = ServerSerializer(read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'server', 'inbound_id', 'client_email',
                  'status', 'data_usage_gb', 'data_limit_gb', 'start_date', 
                  'end_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InboundSerializer(serializers.ModelSerializer):
    """Serializer for the Inbound model"""
    server = ServerSerializer(read_only=True)
    
    class Meta:
        model = Inbound
        fields = ['id', 'server', 'inbound_id', 'protocol', 'tag', 'port', 
                  'network', 'enable', 'expiry_time', 'listen', 'total', 
                  'remark', 'up', 'down', 'last_sync']
        read_only_fields = ['id', 'last_sync']


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for the Client model"""
    inbound = InboundSerializer(read_only=True)
    
    class Meta:
        model = Client
        fields = ['id', 'inbound', 'client_id', 'email', 'enable', 'expiry_time',
                  'total', 'up', 'down', 'subscription_id', 'last_sync']
        read_only_fields = ['id', 'last_sync']


class ClientConfigSerializer(serializers.ModelSerializer):
    """Serializer for the ClientConfig model"""
    client = ClientSerializer(read_only=True)
    
    class Meta:
        model = ClientConfig
        fields = ['id', 'client', 'vmess_link', 'vless_link', 'trojan_link',
                  'shadowsocks_link', 'subscription_url', 'qrcode_data', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SyncLogSerializer(serializers.ModelSerializer):
    """Serializer for the SyncLog model"""
    server = ServerSerializer(read_only=True)
    
    class Meta:
        model = SyncLog
        fields = ['id', 'server', 'status', 'message', 'details', 'created_at']
        read_only_fields = ['id', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for the Transaction model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'status', 'type', 'description',
                  'reference_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reference_id', 'created_at', 'updated_at']


class CardPaymentSerializer(serializers.ModelSerializer):
    """Serializer for the CardPayment model"""
    transaction = TransactionSerializer(read_only=True)
    verified_by = UserSerializer(read_only=True)
    
    class Meta:
        model = CardPayment
        fields = ['id', 'transaction', 'card_number', 'reference_number',
                  'transfer_time', 'verification_code', 'expires_at', 'status',
                  'admin_note', 'verified_by', 'verified_at']
        read_only_fields = ['id', 'verification_code', 'expires_at', 'verified_at']


class ZarinpalPaymentSerializer(serializers.ModelSerializer):
    """Serializer for the ZarinpalPayment model"""
    transaction = TransactionSerializer(read_only=True)
    
    class Meta:
        model = ZarinpalPayment
        fields = ['id', 'transaction', 'authority', 'ref_id', 'status', 'payment_url']
        read_only_fields = ['id', 'authority', 'ref_id', 'payment_url']


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for the PaymentMethod model"""
    
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'type', 'is_active', 'description', 'instructions']
        read_only_fields = ['id']


class DiscountSerializer(serializers.ModelSerializer):
    """Serializer for the Discount model"""
    
    class Meta:
        model = Discount
        fields = ['id', 'code', 'description', 'type', 'value', 'valid_from',
                  'valid_until', 'max_uses', 'times_used', 'is_active', 'created_at']
        read_only_fields = ['id', 'times_used', 'created_at']


class TelegramMessageSerializer(serializers.ModelSerializer):
    """Serializer for the TelegramMessage model"""
    
    class Meta:
        model = TelegramMessage
        fields = ['id', 'name', 'content', 'language_code', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TelegramNotificationSerializer(serializers.ModelSerializer):
    """Serializer for the TelegramNotification model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TelegramNotification
        fields = ['id', 'user', 'type', 'message', 'status', 'error_message',
                  'created_at', 'sent_at']
        read_only_fields = ['id', 'created_at', 'sent_at'] 