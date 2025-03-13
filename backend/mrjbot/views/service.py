from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.translation import gettext_lazy as _

from ..models import Service, Plan, Subscription
from ..serializers import (
    ServiceSerializer,
    PlanSerializer,
    SubscriptionSerializer,
    SubscriptionCreateSerializer,
    SubscriptionUpdateSerializer,
)


class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing services."""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def plans(self, request, pk=None):
        """Get all plans for a service."""
        service = self.get_object()
        plans = Plan.objects.filter(service=service, is_active=True)
        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)


class PlanViewSet(viewsets.ModelViewSet):
    """ViewSet for managing plans."""
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing subscriptions."""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get subscriptions based on user role."""
        if self.request.user.is_staff:
            return Subscription.objects.all()
        return Subscription.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return SubscriptionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SubscriptionUpdateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """Create a new subscription."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a subscription."""
        subscription = self.get_object()
        if subscription.status != 'pending':
            return Response({
                'error': _('Only pending subscriptions can be activated.')
            }, status=status.HTTP_400_BAD_REQUEST)

        subscription.activate()
        return Response(SubscriptionSerializer(subscription).data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a subscription."""
        subscription = self.get_object()
        if subscription.status != 'active':
            return Response({
                'error': _('Only active subscriptions can be deactivated.')
            }, status=status.HTTP_400_BAD_REQUEST)

        subscription.deactivate()
        return Response(SubscriptionSerializer(subscription).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a subscription."""
        subscription = self.get_object()
        if subscription.status not in ['active', 'pending']:
            return Response({
                'error': _('Only active or pending subscriptions can be cancelled.')
            }, status=status.HTTP_400_BAD_REQUEST)

        subscription.cancel()
        return Response(SubscriptionSerializer(subscription).data) 