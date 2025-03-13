from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import LiveChatSession, LiveChatMessage, LiveChatOperator, LiveChatRating
from .serializers import (
    LiveChatSessionSerializer,
    LiveChatMessageSerializer,
    LiveChatOperatorSerializer,
    LiveChatRatingSerializer
)
from main.permissions import (
    IsAdminUser,
    IsSellerUser,
    HasPermission,
    Permission
)

class LiveChatSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chat sessions."""
    serializer_class = LiveChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.has_permission(Permission.MANAGE_CUSTOMERS):
            return LiveChatSession.objects.all()
        return LiveChatSession.objects.filter(user=user)

    def perform_create(self, serializer):
        # Automatically assign available operator
        operators = LiveChatOperator.objects.filter(
            status='online',
            current_sessions__lt=models.F('max_concurrent_sessions')
        ).order_by('current_sessions')
        
        operator = operators.first()
        if operator:
            operator.current_sessions += 1
            operator.save()
            serializer.save(user=self.request.user, operator=operator.user)
        else:
            serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a chat session."""
        session = self.get_object()
        session.status = 'closed'
        session.closed_at = timezone.now()
        session.save()
        return Response({'status': 'closed'})

    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """Transfer chat to another operator."""
        session = self.get_object()
        new_operator_id = request.data.get('operator_id')
        if not new_operator_id:
            return Response(
                {'error': 'New operator ID required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_operator = LiveChatOperator.objects.get(user_id=new_operator_id)
            if new_operator.current_sessions >= new_operator.max_concurrent_sessions:
                return Response(
                    {'error': 'Operator is at maximum capacity'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update operators' session counts
            if session.operator:
                old_operator = LiveChatOperator.objects.get(user=session.operator)
                old_operator.current_sessions -= 1
                old_operator.save()
            
            new_operator.current_sessions += 1
            new_operator.save()
            
            session.operator = new_operator.user
            session.status = 'transferred'
            session.save()
            
            return Response({'status': 'transferred'})
        except LiveChatOperator.DoesNotExist:
            return Response(
                {'error': 'Invalid operator ID'},
                status=status.HTTP_404_NOT_FOUND
            )

class LiveChatMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for chat messages."""
    serializer_class = LiveChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.has_permission(Permission.MANAGE_CUSTOMERS):
            return LiveChatMessage.objects.all()
        return LiveChatMessage.objects.filter(
            Q(session__user=user) | Q(session__operator=user)
        )

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class LiveChatOperatorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chat operators."""
    queryset = LiveChatOperator.objects.all()
    serializer_class = LiveChatOperatorSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Toggle operator's online status."""
        operator = self.get_object()
        new_status = request.data.get('status')
        if new_status in ['online', 'offline', 'busy']:
            operator.status = new_status
            operator.save()
            return Response({'status': new_status})
        return Response(
            {'error': 'Invalid status'},
            status=status.HTTP_400_BAD_REQUEST
        )

class LiveChatRatingViewSet(viewsets.ModelViewSet):
    """ViewSet for chat session ratings."""
    serializer_class = LiveChatRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return LiveChatRating.objects.all()
        return LiveChatRating.objects.filter(
            Q(user=user) | Q(operator=user)
        )

    def perform_create(self, serializer):
        session = serializer.validated_data['session']
        if session.user != self.request.user:
            raise PermissionError("You can only rate your own chat sessions")
        serializer.save(user=self.request.user, operator=session.operator) 