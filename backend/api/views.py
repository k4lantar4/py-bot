from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.db.models import Sum, Count, Q
import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import connection
import redis
import os
import time
import json
import sys
import django
from rest_framework.permissions import AllowAny
import docker
import socket
import psutil
from django.contrib.admin.views.decorators import staff_member_required

from main.models import Server, SubscriptionPlan, Subscription
from v2ray.models import Inbound, Client, SyncLog, ClientConfig
from payments.models import Transaction, CardPayment, ZarinpalPayment, PaymentMethod, Discount
from telegrambot.models import TelegramMessage, TelegramNotification
from v2ray.api_client import sync_server, create_client, delete_client, update_client_traffic, update_client_expiry, reset_client_traffic
from payments.zarinpal import ZarinpalGateway
from payments.card_payment import CardPaymentProcessor

from .serializers import (
    UserSerializer, ServerSerializer, SubscriptionPlanSerializer,
    SubscriptionSerializer, InboundSerializer, ClientSerializer,
    ClientConfigSerializer, SyncLogSerializer, TransactionSerializer,
    CardPaymentSerializer, ZarinpalPaymentSerializer, PaymentMethodSerializer,
    DiscountSerializer, TelegramMessageSerializer, TelegramNotificationSerializer
)

User = get_user_model()

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_admin']
    search_fields = ['username', 'email', 'telegram_id', 'phone_number']
    ordering_fields = ['username', 'date_joined', 'wallet_balance']
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def telegram_auth(self, request):
        """Authenticate or register a user via Telegram ID"""
        telegram_id = request.data.get('telegram_id')
        username = request.data.get('username')
        language_code = request.data.get('language_code', 'fa')
        
        if not telegram_id:
            return Response({'error': 'Telegram ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        try:
            user = User.objects.get(telegram_id=telegram_id)
            # Update user information if needed
            if username and username != user.username:
                user.username = username
            if language_code and language_code != user.language_code:
                user.language_code = language_code
            user.save()
        except User.DoesNotExist:
            # Create new user
            if not username:
                username = f"tg_{telegram_id}"
            
            user = User.objects.create(
                telegram_id=telegram_id,
                username=username,
                language_code=language_code,
                is_active=True
            )
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_telegram_id(self, request):
        """Get user by Telegram ID"""
        telegram_id = request.query_params.get('telegram_id')
        
        if not telegram_id:
            return Response({'error': 'Telegram ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(telegram_id=telegram_id)
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def update_wallet(self, request, pk=None):
        """Update user wallet balance"""
        user = self.get_object()
        amount = request.data.get('amount')
        description = request.data.get('description', 'Manual adjustment')
        admin_id = request.data.get('admin_id')
        
        if amount is None:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
        except ValueError:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create transaction record
        transaction_type = 'deposit' if amount > 0 else 'admin'
        transaction = Transaction.objects.create(
            user=user,
            amount=abs(amount),
            status='completed',
            type=transaction_type,
            description=description
        )
        
        # Update user wallet
        user.wallet_balance += amount
        user.save()
        
        return Response({
            'success': True, 
            'wallet_balance': user.wallet_balance,
            'transaction_id': transaction.id
        })

    @swagger_auto_schema(
        operation_description="Get user profile",
        responses={
            200: UserSerializer,
            404: "User not found"
        }
    )
    @action(detail=False, methods=['get'])
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update user profile",
        request_body=UserSerializer,
        responses={
            200: UserSerializer,
            400: "Bad request"
        }
    )
    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ServerViewSet(viewsets.ModelViewSet):
    """API endpoint for servers"""
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'url']
    ordering_fields = ['name', 'created_at']
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Sync server with 3x-UI panel"""
        server = self.get_object()
        
        # Sync server
        result = sync_server(server.id)
        
        if result:
            return Response({'success': True, 'message': 'Server synced successfully'})
        else:
            return Response({'success': False, 'message': 'Failed to sync server'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def inbounds(self, request, pk=None):
        """Get server inbounds"""
        server = self.get_object()
        inbounds = Inbound.objects.filter(server=server)
        serializer = InboundSerializer(inbounds, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def sync_logs(self, request, pk=None):
        """Get server sync logs"""
        server = self.get_object()
        sync_logs = SyncLog.objects.filter(server=server).order_by('-created_at')[:10]
        serializer = SyncLogSerializer(sync_logs, many=True)
        return Response(serializer.data)


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    """API endpoint for subscription plans"""
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'type']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']


class SubscriptionViewSet(viewsets.ModelViewSet):
    """API endpoint for subscriptions"""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'user', 'plan', 'server']
    search_fields = ['user__username', 'client_email']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def purchase(self, request):
        """Purchase a subscription"""
        user_id = request.data.get('user_id')
        plan_id = request.data.get('plan_id')
        server_id = request.data.get('server_id')
        payment_type = request.data.get('payment_type', 'wallet')
        
        if not all([user_id, plan_id, server_id]):
            return Response({
                'error': 'User ID, plan ID, and server ID are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
            server = Server.objects.get(id=server_id, is_active=True)
        except (User.DoesNotExist, SubscriptionPlan.DoesNotExist, Server.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate start and end dates
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(days=plan.duration_days)
        
        # Check payment type
        if payment_type == 'wallet':
            # Check wallet balance
            if user.wallet_balance < plan.price:
                return Response({
                    'error': 'Insufficient wallet balance',
                    'required': plan.price,
                    'available': user.wallet_balance
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create subscription
            subscription = Subscription.objects.create(
                user=user,
                plan=plan,
                server=server,
                data_limit_gb=plan.data_limit_gb,
                start_date=start_date,
                end_date=end_date,
                status='active'
            )
            
            # Create payment record
            payment = Transaction.objects.create(
                user=user,
                amount=plan.price,
                status='completed',
                type='deposit',
                description=f"Purchase of {plan.name} plan"
            )
            
            # Update user wallet
            user.wallet_balance -= plan.price
            user.save()
            
            # Create client on 3x-UI
            create_client(subscription.id)
            
            serializer = self.get_serializer(subscription)
            return Response({
                'success': True,
                'subscription': serializer.data,
                'payment_id': payment.id,
                'remaining_balance': user.wallet_balance
            })
        else:
            # Create pending subscription
            subscription = Subscription.objects.create(
                user=user,
                plan=plan,
                server=server,
                data_limit_gb=plan.data_limit_gb,
                start_date=start_date,
                end_date=end_date,
                status='pending'
            )
            
            # Create payment record
            payment = Transaction.objects.create(
                user=user,
                amount=plan.price,
                status='pending',
                type=payment_type,
                description=f"Purchase of {plan.name} plan"
            )
            
            serializer = self.get_serializer(subscription)
            return Response({
                'success': True,
                'subscription': serializer.data,
                'payment_id': payment.id,
                'requires_payment': True
            })
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_config(self, request, pk=None):
        """Get subscription configuration"""
        subscription = self.get_object()
        
        # Check if subscription belongs to user or user is admin
        if subscription.user.id != request.user.id and not request.user.is_admin:
            return Response({'error': 'You are not authorized to view this subscription'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        if subscription.status != 'active':
            return Response({'error': 'Subscription is not active'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get client config
        configs = ClientConfig.objects.filter(
            client__subscription_id=subscription.id
        ).first()
        
        if not configs:
            return Response({'error': 'Configuration not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ClientConfigSerializer(configs)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get user subscriptions",
        responses={
            200: SubscriptionSerializer(many=True),
            404: "User not found"
        }
    )
    @action(detail=False, methods=['get'])
    def user_subscriptions(self, request):
        subscriptions = self.queryset.filter(user=request.user)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)


class InboundViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for inbounds (read-only)"""
    queryset = Inbound.objects.all()
    serializer_class = InboundSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['server', 'protocol', 'enable']
    search_fields = ['tag', 'remark']
    ordering_fields = ['port', 'last_sync']
    
    @action(detail=True, methods=['get'])
    def clients(self, request, pk=None):
        """Get inbound clients"""
        inbound = self.get_object()
        clients = Client.objects.filter(inbound=inbound)
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)


class ClientViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for clients (read-only)"""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['inbound', 'enable']
    search_fields = ['email', 'client_id']
    ordering_fields = ['expiry_time', 'last_sync']
    
    @action(detail=True, methods=['get'])
    def config(self, request, pk=None):
        """Get client config"""
        client = self.get_object()
        try:
            config = ClientConfig.objects.get(client=client)
            serializer = ClientConfigSerializer(config)
            return Response(serializer.data)
        except ClientConfig.DoesNotExist:
            return Response({'error': 'Config not found'}, status=status.HTTP_404_NOT_FOUND)


class TransactionViewSet(viewsets.ModelViewSet):
    """API endpoint for transactions"""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'status', 'type']
    search_fields = ['user__username', 'reference_id', 'description']
    ordering_fields = ['amount', 'created_at']
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def create_payment(self, request):
        """Create a new payment transaction"""
        user_id = request.data.get('user_id')
        amount = request.data.get('amount')
        payment_type = request.data.get('payment_type', 'card')
        subscription_id = request.data.get('subscription_id')
        description = request.data.get('description', 'Wallet deposit')
        payment_data = request.data.get('payment_data', {})
        
        if not all([user_id, amount]):
            return Response({
                'error': 'User ID and amount are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            amount = float(amount)
            
            if subscription_id:
                subscription = Subscription.objects.get(id=subscription_id)
            else:
                subscription = None
                
        except (User.DoesNotExist, Subscription.DoesNotExist, ValueError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create transaction
        transaction = Transaction.objects.create(
            user=user,
            amount=amount,
            status='pending',
            type='deposit' if not subscription_id else 'purchase',
            description=description
        )
        
        # Process based on payment type
        if payment_type == 'card':
            # Create card payment
            card_number = payment_data.get('card_number')
            reference_number = payment_data.get('reference_number')
            transfer_time = payment_data.get('transfer_time')
            
            if not all([card_number, reference_number, transfer_time]):
                transaction.delete()
                return Response({
                    'error': 'Card number, reference number, and transfer time are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                transfer_time = timezone.datetime.fromisoformat(transfer_time)
            except ValueError:
                transaction.delete()
                return Response({
                    'error': 'Invalid transfer time format'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            card_payment = CardPayment.objects.create(
                transaction=transaction,
                card_number=card_number,
                reference_number=reference_number,
                transfer_time=transfer_time,
                status='pending'
            )
            
            return Response({
                'success': True,
                'transaction_id': transaction.id,
                'reference_id': transaction.reference_id,
                'verification_code': card_payment.verification_code
            })
            
        elif payment_type == 'zarinpal':
            # Setup Zarinpal payment
            from payments.zarinpal import ZarinpalGateway
            
            callback_url = payment_data.get('callback_url', '')
            gateway = ZarinpalGateway()
            result = gateway.request_payment(
                transaction.id,
                amount,
                description,
                user.email,
                user.phone_number
            )
            
            if result.get('success'):
                return Response({
                    'success': True,
                    'transaction_id': transaction.id,
                    'reference_id': transaction.reference_id,
                    'payment_url': result.get('payment_url')
                })
            else:
                transaction.delete()
                return Response({
                    'error': result.get('error_message', 'Payment gateway error')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            transaction.delete()
            return Response({
                'error': f'Unsupported payment type: {payment_type}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def verify_payment(self, request):
        """Verify a payment transaction"""
        payment_type = request.data.get('payment_type', 'card')
        reference_id = request.data.get('reference_id')
        verification_data = request.data.get('verification_data', {})
        
        if not reference_id:
            return Response({'error': 'Reference ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            transaction = Transaction.objects.get(reference_id=reference_id)
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if transaction.status == 'completed':
            return Response({'status': 'already_verified', 'transaction_id': transaction.id})
        
        if payment_type == 'card':
            # Verify card payment
            verification_code = verification_data.get('verification_code')
            
            if not verification_code:
                return Response({'error': 'Verification code is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                card_payment = CardPayment.objects.get(
                    transaction=transaction,
                    verification_code=verification_code
                )
            except CardPayment.DoesNotExist:
                return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
            
            if card_payment.status == 'verified':
                return Response({'status': 'already_verified', 'transaction_id': transaction.id})
            
            if card_payment.is_expired():
                card_payment.status = 'expired'
                card_payment.save()
                transaction.status = 'expired'
                transaction.save()
                return Response({'error': 'Payment verification expired'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Payment needs manual verification by admin
            return Response({
                'status': 'pending_verification',
                'transaction_id': transaction.id,
                'message': 'Your payment is pending verification by an administrator.'
            })
            
        elif payment_type == 'zarinpal':
            # Verify Zarinpal payment
            from payments.zarinpal import ZarinpalGateway
            
            authority = verification_data.get('authority')
            
            if not authority:
                return Response({'error': 'Authority is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                zarinpal_payment = ZarinpalPayment.objects.get(
                    authority=authority
                )
            except ZarinpalPayment.DoesNotExist:
                return Response({'error': 'Invalid authority'}, status=status.HTTP_400_BAD_REQUEST)
            
            gateway = ZarinpalGateway()
            result = gateway.verify_payment(authority, transaction.amount)
            
            if result.get('success'):
                # Update subscription if this was a subscription payment
                if transaction.type == 'purchase' and transaction.subscription:
                    subscription = transaction.subscription
                    subscription.status = 'active'
                    subscription.save()
                    
                    # Create client on 3x-UI
                    create_client(subscription.id)
                
                # Update user wallet if this was a deposit
                if transaction.type == 'deposit':
                    user = transaction.user
                    user.wallet_balance += transaction.amount
                    user.save()
                
                return Response({
                    'status': 'completed',
                    'transaction_id': transaction.id,
                    'ref_id': result.get('ref_id')
                })
            else:
                return Response({
                    'error': result.get('error_message', 'Payment verification failed')
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': f'Unsupported payment type: {payment_type}'
            }, status=status.HTTP_400_BAD_REQUEST)


class CardPaymentViewSet(viewsets.ModelViewSet):
    """API endpoint for card payments"""
    queryset = CardPayment.objects.all()
    serializer_class = CardPaymentSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'transaction__user']
    search_fields = ['verification_code', 'card_number', 'reference_number']
    ordering_fields = ['transfer_time', 'created_at']
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a card payment"""
        card_payment = self.get_object()
        admin_note = request.data.get('admin_note', '')
        
        # Verify payment
        processor = CardPaymentProcessor()
        result = processor.verify_payment(card_payment.verification_code, request.user, admin_note)
        
        if result.get('success'):
            return Response({'success': True, 'message': result.get('message')})
        else:
            return Response({'success': False, 'message': result.get('error_message')}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a card payment"""
        card_payment = self.get_object()
        admin_note = request.data.get('admin_note', '')
        
        # Reject payment
        processor = CardPaymentProcessor()
        result = processor.reject_payment(card_payment.verification_code, request.user, admin_note)
        
        if result.get('success'):
            return Response({'success': True, 'message': result.get('message')})
        else:
            return Response({'success': False, 'message': result.get('error_message')}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending card payments"""
        processor = CardPaymentProcessor()
        result = processor.get_pending_payments()
        
        if result.get('success'):
            return Response({'success': True, 'payments': result.get('payments')})
        else:
            return Response({'success': False, 'message': result.get('error_message')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def expire_old(self, request):
        """Expire old pending card payments"""
        processor = CardPaymentProcessor()
        result = processor.expire_old_payments()
        
        if result.get('success'):
            return Response({'success': True, 'expired_count': result.get('expired_count')})
        else:
            return Response({'success': False, 'message': result.get('error_message')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ZarinpalPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for Zarinpal payments (read-only)"""
    queryset = ZarinpalPayment.objects.all()
    serializer_class = ZarinpalPaymentSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'transaction__user']
    search_fields = ['authority', 'ref_id']
    ordering_fields = ['created_at']


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """API endpoint for payment methods"""
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'type']
    search_fields = ['name', 'description']
    ordering_fields = ['name']


class DiscountViewSet(viewsets.ModelViewSet):
    """API endpoint for discounts"""
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'type']
    search_fields = ['code', 'description']
    ordering_fields = ['code', 'value', 'valid_until', 'created_at']
    
    @action(detail=True, methods=['get'])
    def validate(self, request, pk=None):
        """Validate a discount code"""
        discount = self.get_object()
        
        if discount.is_valid():
            return Response({'valid': True, 'discount': self.get_serializer(discount).data})
        else:
            return Response({'valid': False, 'reason': 'Discount code is not valid'})


class TelegramMessageViewSet(viewsets.ModelViewSet):
    """API endpoint for Telegram messages"""
    queryset = TelegramMessage.objects.all()
    serializer_class = TelegramMessageSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['language_code']
    search_fields = ['name', 'content']
    ordering_fields = ['name', 'created_at']


class TelegramNotificationViewSet(viewsets.ModelViewSet):
    """API endpoint for Telegram notifications"""
    queryset = TelegramNotification.objects.all()
    serializer_class = TelegramNotificationSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'type', 'status']
    search_fields = ['message']
    ordering_fields = ['created_at', 'sent_at']


# Add a BotConfig endpoint that returns configuration for the Telegram bot
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings

class BotConfigView(APIView):
    """API endpoint for bot configuration"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get bot configuration"""
        # Get available payment methods
        payment_methods = PaymentMethod.objects.filter(is_active=True)
        payment_method_serializer = PaymentMethodSerializer(payment_methods, many=True)
        
        # Get subscription plans
        subscription_plans = SubscriptionPlan.objects.filter(is_active=True)
        plan_serializer = SubscriptionPlanSerializer(subscription_plans, many=True)
        
        # Get card payment details
        card_number = getattr(settings, 'CARD_PAYMENT_NUMBER', '')
        card_holder = getattr(settings, 'CARD_PAYMENT_HOLDER', '')
        bank_name = getattr(settings, 'CARD_PAYMENT_BANK', '')
        
        # Get message templates
        messages = TelegramMessage.objects.all()
        message_serializer = TelegramMessageSerializer(messages, many=True)
        
        # Return configuration
        return Response({
            'payment_methods': payment_method_serializer.data,
            'subscription_plans': plan_serializer.data,
            'card_payment': {
                'card_number': card_number,
                'card_holder': card_holder,
                'bank_name': bank_name
            },
            'messages': message_serializer.data,
            'bot_settings': {
                'admin_telegram_ids': getattr(settings, 'ADMIN_TELEGRAM_IDS', []),
                'default_language': getattr(settings, 'DEFAULT_LANGUAGE', 'fa'),
                'support_contact': getattr(settings, 'SUPPORT_CONTACT', ''),
                'maintenance_mode': getattr(settings, 'MAINTENANCE_MODE', False)
            }
        })


class PlanSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for retrieving plan suggestions."""
    serializer_class = PlanSuggestionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PlanSuggestion.objects.filter(
            user=self.request.user,
            is_accepted=False
        ).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a plan suggestion."""
        suggestion = self.get_object()
        suggestion.accept()
        return Response({'status': 'accepted'})


class PointsRedemptionRuleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for retrieving points redemption rules."""
    queryset = PointsRedemptionRule.objects.filter(is_active=True)
    serializer_class = PointsRedemptionRuleSerializer
    permission_classes = [permissions.IsAuthenticated]


class PointsRedemptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing points redemptions."""
    serializer_class = PointsRedemptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PointsRedemption.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create a new points redemption."""
        rule_id = request.data.get('rule_id')
        applied_to_id = request.data.get('applied_to_id')
        
        try:
            rule = PointsRedemptionRule.objects.get(id=rule_id, is_active=True)
            user = request.user
            
            # Check if user has enough points
            if user.points < rule.points_cost:
                return Response({
                    'error': 'Insufficient points',
                    'required': rule.points_cost,
                    'available': user.points
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get subscription if needed
            applied_to = None
            if rule.reward_type in ['data', 'days'] and applied_to_id:
                try:
                    applied_to = Subscription.objects.get(
                        id=applied_to_id,
                        user=user,
                        status='active'
                    )
                except Subscription.DoesNotExist:
                    return Response({
                        'error': 'Active subscription not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Create redemption
            redemption = PointsRedemption.objects.create(
                user=user,
                rule=rule,
                points_spent=rule.points_cost,
                reward_value=rule.reward_value,
                applied_to=applied_to
            )
            
            # Deduct points
            user.points -= rule.points_cost
            user.save()
            
            # Apply reward
            if redemption.apply_reward():
                serializer = self.get_serializer(redemption)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # Refund points if reward application failed
                user.points += rule.points_cost
                user.save()
                redemption.delete()
                return Response({
                    'error': 'Failed to apply reward'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except PointsRedemptionRule.DoesNotExist:
            return Response({
                'error': 'Invalid redemption rule'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a points redemption."""
        redemption = self.get_object()
        
        if redemption.status != 'pending':
            return Response({
                'error': 'Can only cancel pending redemptions'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Refund points
        request.user.points += redemption.points_spent
        request.user.save()
        
        redemption.status = 'cancelled'
        redemption.save()
        
        return Response({'status': 'cancelled'})


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring the backend API
    """
    # Get startup time
    startup_time = getattr(health_check, 'startup_time', datetime.now())
    if not hasattr(health_check, 'startup_time'):
        health_check.startup_time = startup_time
    
    # Calculate uptime
    uptime_seconds = (datetime.now() - health_check.startup_time).total_seconds()
    
    # Check database
    db_status = 'healthy'
    db_error = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        db_status = 'unhealthy'
        db_error = str(e)
    
    # Check Redis
    redis_status = 'healthy'
    redis_error = None
    try:
        # Get Redis connection details from environment
        redis_host = os.environ.get("REDIS_HOST", "redis")
        redis_port = int(os.environ.get("REDIS_PORT", "6379"))
        redis_db = int(os.environ.get("REDIS_DB", "0"))
        redis_password = os.environ.get("REDIS_PASSWORD", "")
        
        # Try to connect and ping
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password or None,
            socket_timeout=2
        )
        r.ping()
    except Exception as e:
        redis_status = 'unhealthy'
        redis_error = str(e)
    
    # System info
    system_info = {
        'python_version': sys.version,
        'django_version': django.get_version(),
        'platform': sys.platform,
    }
    
    # Build response
    response_data = {
        'status': 'ok' if db_status == 'healthy' and redis_status == 'healthy' else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': uptime_seconds,
        'components': {
            'database': {
                'status': db_status,
                'error': db_error
            },
            'redis': {
                'status': redis_status,
                'error': redis_error
            }
        },
        'system': system_info
    }
    
    status_code = 200 if response_data['status'] == 'ok' else 500
    return Response(response_data, status=status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def container_metrics(request):
    """
    Get metrics for all Docker containers in the MRJBot system
    """
    try:
        # Try to connect to Docker socket
        client = docker.from_env()
        
        # Get all containers with mrjbot in their name
        containers = client.containers.list(all=True, filters={"name": "mrjbot"})
        
        # System stats
        system_stats = {
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "hostname": socket.gethostname(),
            "uptime_seconds": int(time.time() - psutil.boot_time())
        }
        
        # Format container data
        container_data = []
        for container in containers:
            stats = container.stats(stream=False)
            
            # Calculate CPU usage percentage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_percent = 0.0
            if system_cpu_delta > 0 and cpu_delta > 0:
                cpu_percent = (cpu_delta / system_cpu_delta) * 100.0 * len(stats['cpu_stats']['cpu_usage']['percpu_usage'])
                
            # Calculate memory usage percentage
            memory_percent = 0.0
            if 'memory_stats' in stats and 'usage' in stats['memory_stats'] and 'limit' in stats['memory_stats']:
                memory_percent = (stats['memory_stats']['usage'] / stats['memory_stats']['limit']) * 100.0
                
            # Get container start time
            start_time = datetime.fromtimestamp(container.attrs['Created'])
            
            # Get container logs (last 5 lines)
            logs = container.logs(tail=5, timestamps=True).decode('utf-8').strip().split('\n')
            if logs == ['']:
                logs = []
                
            container_data.append({
                "id": container.id[:12],
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else container.image.id[:12],
                "status": container.status,
                "state": container.attrs['State'],
                "created": start_time.isoformat(),
                "uptime": str(datetime.now() - start_time).split('.')[0],
                "ports": container.ports,
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory_percent, 2),
                "recent_logs": logs
            })
            
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "system": system_stats,
            "containers": container_data
        }
            
        return Response(response_data)
    except docker.errors.DockerException as e:
        return Response({
            "error": "Docker API error",
            "detail": str(e),
            "help": "Make sure Docker is running and the API can access the Docker socket"
        }, status=500)
    except Exception as e:
        return Response({
            "error": "Error fetching container metrics",
            "detail": str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def database_metrics(request):
    """
    Get detailed metrics about the PostgreSQL database
    """
    try:
        from django.db import connections, connection
        from django.apps import apps
        
        # Get database connection details
        db_host = os.environ.get("DB_HOST", "postgres")
        db_port = os.environ.get("DB_PORT", "5432")
        
        # Get database stats
        with connection.cursor() as cursor:
            # Get PostgreSQL version
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            # Get database size
            cursor.execute("SELECT pg_database_size(current_database());")
            db_size_bytes = cursor.fetchone()[0]
            
            # Get connection count
            cursor.execute("""
                SELECT count(*) FROM pg_stat_activity 
                WHERE datname = current_database();
            """)
            connection_count = cursor.fetchone()[0]
            
            # Get table statistics
            cursor.execute("""
                SELECT relname, n_live_tup, n_dead_tup, last_vacuum, last_analyze
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC;
            """)
            table_stats = []
            for row in cursor.fetchall():
                table_stats.append({
                    "table_name": row[0],
                    "row_count": row[1],
                    "dead_rows": row[2],
                    "last_vacuum": row[3].isoformat() if row[3] else None,
                    "last_analyze": row[4].isoformat() if row[4] else None,
                })
        
        # Get model stats
        model_stats = []
        for model in apps.get_models():
            if model._meta.app_label not in ('admin', 'auth', 'contenttypes', 'sessions'):
                try:
                    model_stats.append({
                        "model": f"{model._meta.app_label}.{model._meta.model_name}",
                        "row_count": model.objects.count(),
                        "fields": len(model._meta.fields),
                    })
                except:
                    pass
        
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "version": version,
            "host": db_host,
            "port": db_port,
            "size_bytes": db_size_bytes,
            "size_mb": round(db_size_bytes / (1024 * 1024), 2),
            "connections": connection_count,
            "tables": table_stats,
            "models": model_stats,
        }
            
        return Response(response_data)
    except Exception as e:
        return Response({
            "error": "Error fetching database metrics",
            "detail": str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def redis_metrics(request):
    """
    Get detailed metrics about the Redis server
    """
    try:
        import redis
        
        # Get Redis connection details from environment
        redis_host = os.environ.get("REDIS_HOST", "redis")
        redis_port = int(os.environ.get("REDIS_PORT", "6379"))
        redis_db = int(os.environ.get("REDIS_DB", "0"))
        redis_password = os.environ.get("REDIS_PASSWORD", "")
        
        # Connect to Redis
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password or None,
            socket_timeout=2
        )
        
        # Get Redis info
        info = r.info()
        
        # Get key count and sample keys
        db_key = f"db{redis_db}"
        key_count = info.get(db_key, {}).get('keys', 0)
        
        # Get some key samples (max 10)
        key_samples = []
        scan_iter = r.scan_iter(count=10)
        for i, key in enumerate(scan_iter):
            if i >= 10:
                break
            key_str = key.decode('utf-8')
            key_type = r.type(key).decode('utf-8')
            key_ttl = r.ttl(key)
            
            # Get type-specific info
            key_detail = {"type": key_type, "ttl": key_ttl}
            if key_type == "string":
                try:
                    value = r.get(key).decode('utf-8')
                    if len(value) > 100:
                        value = value[:100] + "..."
                    key_detail["value"] = value
                except:
                    key_detail["value"] = "<binary data>"
            elif key_type == "list":
                key_detail["length"] = r.llen(key)
            elif key_type == "hash":
                key_detail["length"] = r.hlen(key)
            elif key_type == "set":
                key_detail["length"] = r.scard(key)
            elif key_type == "zset":
                key_detail["length"] = r.zcard(key)
                
            key_samples.append({
                "key": key_str,
                "details": key_detail
            })
            
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "host": redis_host,
            "port": redis_port,
            "version": info.get('redis_version'),
            "uptime_seconds": info.get('uptime_in_seconds'),
            "clients_connected": info.get('connected_clients'),
            "memory_used_bytes": info.get('used_memory'),
            "memory_used_mb": round(int(info.get('used_memory', 0)) / (1024 * 1024), 2),
            "memory_peak_mb": round(int(info.get('used_memory_peak', 0)) / (1024 * 1024), 2),
            "key_count": key_count,
            "key_samples": key_samples,
            "stats": {
                "commands_processed": info.get('total_commands_processed'),
                "keyspace_hits": info.get('keyspace_hits'),
                "keyspace_misses": info.get('keyspace_misses'),
                "expired_keys": info.get('expired_keys'),
                "evicted_keys": info.get('evicted_keys'),
            }
        }
            
        return Response(response_data)
    except Exception as e:
        return Response({
            "error": "Error fetching Redis metrics",
            "detail": str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_metrics(request):
    """
    Get detailed system metrics including CPU, memory, disk, and network
    """
    try:
        import psutil
        
        # Get CPU info
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_times = psutil.cpu_times_percent(interval=0.5)
        
        # Get memory info
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()
        
        # Get disk info
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Get network info
        net_io = psutil.net_io_counters()
        net_connections = len(psutil.net_connections())
        
        # Get process info
        process_count = len(psutil.pids())
        
        # Get load average
        load_avg = psutil.getloadavg()
        
        # Get boot time
        boot_time = datetime.fromtimestamp(psutil.boot_time()).isoformat()
        uptime_seconds = int(time.time() - psutil.boot_time())
        
        # Format response
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "hostname": socket.gethostname(),
            "boot_time": boot_time,
            "uptime_seconds": uptime_seconds,
            "cpu": {
                "percent_per_core": cpu_percent,
                "average": sum(cpu_percent) / len(cpu_percent),
                "cores": len(cpu_percent),
                "times_percent": {
                    "user": cpu_times.user,
                    "system": cpu_times.system,
                    "idle": cpu_times.idle,
                }
            },
            "memory": {
                "total_mb": round(virtual_memory.total / (1024 * 1024), 2),
                "available_mb": round(virtual_memory.available / (1024 * 1024), 2),
                "used_mb": round(virtual_memory.used / (1024 * 1024), 2),
                "percent": virtual_memory.percent,
                "swap_total_mb": round(swap_memory.total / (1024 * 1024), 2),
                "swap_used_mb": round(swap_memory.used / (1024 * 1024), 2),
                "swap_percent": swap_memory.percent,
            },
            "disk": {
                "total_gb": round(disk_usage.total / (1024 * 1024 * 1024), 2),
                "used_gb": round(disk_usage.used / (1024 * 1024 * 1024), 2),
                "free_gb": round(disk_usage.free / (1024 * 1024 * 1024), 2),
                "percent": disk_usage.percent,
                "read_mb": round(disk_io.read_bytes / (1024 * 1024), 2),
                "write_mb": round(disk_io.write_bytes / (1024 * 1024), 2),
            },
            "network": {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024 * 1024), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024 * 1024), 2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "connections": net_connections,
            },
            "load_average": {
                "1min": load_avg[0],
                "5min": load_avg[1],
                "15min": load_avg[2],
            },
            "processes": {
                "count": process_count,
            }
        }
            
        return Response(response_data)
    except Exception as e:
        return Response({
            "error": "Error fetching system metrics",
            "detail": str(e)
        }, status=500)


@staff_member_required
def monitoring_dashboard(request):
    """
    Admin monitoring dashboard showing system metrics
    """
    return render(request, 'admin/monitoring_dashboard.html')
