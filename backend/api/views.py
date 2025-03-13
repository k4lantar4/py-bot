from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from main.models import Server, SubscriptionPlan, Subscription
from v2ray.models import Inbound, Client, SyncLog, ClientConfig
from payments.models import Transaction, CardPayment, ZarinpalPayment, PaymentMethod, Discount
from telegram.models import TelegramMessage, TelegramNotification
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
    filterset_fields = ['is_active', 'is_admin', 'language_code']
    search_fields = ['username', 'email', 'telegram_id', 'phone_number']
    ordering_fields = ['username', 'date_joined', 'wallet_balance']
    
    @action(detail=True, methods=['post'])
    def add_balance(self, request, pk=None):
        """Add balance to user wallet"""
        user = self.get_object()
        amount = request.data.get('amount')
        
        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.wallet_balance += amount
            user.save()
            
            # Create transaction
            Transaction.objects.create(
                user=user,
                amount=amount,
                status='completed',
                type='admin',
                description='Admin added balance to wallet'
            )
            
            return Response({'success': True, 'new_balance': user.wallet_balance})
        except ValueError:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def deduct_balance(self, request, pk=None):
        """Deduct balance from user wallet"""
        user = self.get_object()
        amount = request.data.get('amount')
        
        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
            
            if user.wallet_balance < amount:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.wallet_balance -= amount
            user.save()
            
            # Create transaction
            Transaction.objects.create(
                user=user,
                amount=amount,
                status='completed',
                type='admin',
                description='Admin deducted balance from wallet'
            )
            
            return Response({'success': True, 'new_balance': user.wallet_balance})
        except ValueError:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user"""
        serializer = self.get_serializer(request.user)
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
    
    @action(detail=True, methods=['post'])
    def create_client(self, request, pk=None):
        """Create client in 3x-UI panel"""
        subscription = self.get_object()
        
        # Create client
        result = create_client(subscription.id)
        
        if result:
            return Response({'success': True, 'message': 'Client created successfully'})
        else:
            return Response({'success': False, 'message': 'Failed to create client'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def delete_client(self, request, pk=None):
        """Delete client from 3x-UI panel"""
        subscription = self.get_object()
        
        # Delete client
        result = delete_client(subscription.id)
        
        if result:
            return Response({'success': True, 'message': 'Client deleted successfully'})
        else:
            return Response({'success': False, 'message': 'Failed to delete client'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def update_traffic(self, request, pk=None):
        """Update client traffic limit"""
        subscription = self.get_object()
        traffic_limit_gb = request.data.get('traffic_limit_gb')
        
        if not traffic_limit_gb:
            return Response({'error': 'Traffic limit is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            traffic_limit_gb = int(traffic_limit_gb)
            
            # Update client traffic
            result = update_client_traffic(subscription.id, traffic_limit_gb)
            
            if result:
                return Response({'success': True, 'message': 'Client traffic updated successfully'})
            else:
                return Response({'success': False, 'message': 'Failed to update client traffic'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValueError:
            return Response({'error': 'Invalid traffic limit'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_expiry(self, request, pk=None):
        """Update client expiry time"""
        subscription = self.get_object()
        days = request.data.get('days')
        
        if not days:
            return Response({'error': 'Days is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            days = int(days)
            
            # Calculate new expiry time
            expiry_time = timezone.now() + timedelta(days=days)
            
            # Update client expiry
            result = update_client_expiry(subscription.id, expiry_time)
            
            if result:
                return Response({'success': True, 'message': 'Client expiry updated successfully'})
            else:
                return Response({'success': False, 'message': 'Failed to update client expiry'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValueError:
            return Response({'error': 'Invalid days'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reset_traffic(self, request, pk=None):
        """Reset client traffic usage"""
        subscription = self.get_object()
        
        # Reset client traffic
        result = reset_client_traffic(subscription.id)
        
        if result:
            return Response({'success': True, 'message': 'Client traffic reset successfully'})
        else:
            return Response({'success': False, 'message': 'Failed to reset client traffic'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
