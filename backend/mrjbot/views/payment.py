from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.translation import gettext_lazy as _

from ..models import Payment, Transaction, Commission, WithdrawalRequest
from ..serializers import (
    PaymentSerializer,
    PaymentCreateSerializer,
    TransactionSerializer,
    CommissionSerializer,
    WithdrawalRequestSerializer,
    WithdrawalRequestCreateSerializer,
)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payments."""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get payments based on user role."""
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """Create a new payment."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a payment."""
        payment = self.get_object()
        if payment.status != 'pending':
            return Response({
                'error': _('Only pending payments can be verified.')
            }, status=status.HTTP_400_BAD_REQUEST)

        payment.verify()
        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a payment."""
        payment = self.get_object()
        if payment.status != 'pending':
            return Response({
                'error': _('Only pending payments can be cancelled.')
            }, status=status.HTTP_400_BAD_REQUEST)

        payment.cancel()
        return Response(PaymentSerializer(payment).data)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing transactions."""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get transactions based on user role."""
        if self.request.user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(user=self.request.user)


class CommissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing commissions."""
    serializer_class = CommissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get commissions based on user role."""
        if self.request.user.is_staff:
            return Commission.objects.all()
        return Commission.objects.filter(seller=self.request.user)


class WithdrawalRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing withdrawal requests."""
    serializer_class = WithdrawalRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get withdrawal requests based on user role."""
        if self.request.user.is_staff:
            return WithdrawalRequest.objects.all()
        return WithdrawalRequest.objects.filter(seller=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return WithdrawalRequestCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """Create a new withdrawal request."""
        serializer.save(seller=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a withdrawal request."""
        withdrawal = self.get_object()
        if withdrawal.status != 'pending':
            return Response({
                'error': _('Only pending withdrawal requests can be approved.')
            }, status=status.HTTP_400_BAD_REQUEST)

        withdrawal.approve()
        return Response(WithdrawalRequestSerializer(withdrawal).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        """Reject a withdrawal request."""
        withdrawal = self.get_object()
        if withdrawal.status != 'pending':
            return Response({
                'error': _('Only pending withdrawal requests can be rejected.')
            }, status=status.HTTP_400_BAD_REQUEST)

        withdrawal.reject()
        return Response(WithdrawalRequestSerializer(withdrawal).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def complete(self, request, pk=None):
        """Complete a withdrawal request."""
        withdrawal = self.get_object()
        if withdrawal.status != 'approved':
            return Response({
                'error': _('Only approved withdrawal requests can be completed.')
            }, status=status.HTTP_400_BAD_REQUEST)

        withdrawal.complete()
        return Response(WithdrawalRequestSerializer(withdrawal).data) 