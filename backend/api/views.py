from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.db.models import Sum, Count, Q
import datetime

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
