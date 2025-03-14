from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import PointsTransaction, PointsRedemptionRule, PointsRedemption
from .services import PointsService
from .serializers import (
    PointsTransactionSerializer,
    PointsRedemptionRuleSerializer,
    PointsRedemptionSerializer
)

class PointsTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for points transactions."""
    serializer_class = PointsTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PointsTransaction.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get current points balance."""
        points = PointsService.get_user_points(request.user)
        return Response({'points': points})
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get transaction history."""
        limit = int(request.query_params.get('limit', 10))
        transactions = PointsService.get_user_transactions(request.user, limit)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

class PointsRedemptionRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for points redemption rules."""
    serializer_class = PointsRedemptionRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PointsRedemptionRule.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available rewards for current user."""
        rules = PointsService.get_available_rewards(request.user)
        serializer = self.get_serializer(rules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def redeem(self, request, pk=None):
        """Redeem points for a reward."""
        try:
            redemption = PointsService.redeem_points(request.user, pk)
            serializer = PointsRedemptionSerializer(redemption)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PointsRedemptionViewSet(viewsets.ModelViewSet):
    """ViewSet for points redemptions."""
    serializer_class = PointsRedemptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PointsRedemption.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get redemption history."""
        limit = int(request.query_params.get('limit', 10))
        redemptions = PointsService.get_user_redemptions(request.user, limit)
        serializer = self.get_serializer(redemptions, many=True)
        return Response(serializer.data) 