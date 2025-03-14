from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import Service, Plan, Subscription, Config, Usage, ServiceLog, ServiceMetric, ServiceAlert
from .serializers import (
    ServiceSerializer,
    PlanSerializer,
    SubscriptionSerializer,
    ConfigSerializer,
    UsageSerializer,
    ServiceLogSerializer,
    ServiceMetricSerializer,
    ServiceAlertSerializer,
)
from .permissions import IsServiceOwner, IsServiceAdmin, HasValidSubscription

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Service.objects.all()
        return Service.objects.filter(is_active=True)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        service = self.get_object()
        return Response({
            'status': 'active' if service.is_active else 'inactive',
            'last_check': timezone.now(),
        })
    
    @action(detail=True, methods=['get'])
    def usage(self, request, pk=None):
        service = self.get_object()
        subscription = Subscription.objects.filter(
            user=request.user,
            plan__service=service,
            status='active'
        ).first()
        
        if not subscription:
            return Response({
                'error': 'No active subscription found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        usage = Usage.objects.filter(subscription=subscription)
        serializer = UsageSerializer(usage, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def config(self, request, pk=None):
        service = self.get_object()
        configs = Config.objects.filter(service=service, is_active=True)
        serializer = ConfigSerializer(configs, many=True)
        return Response(serializer.data)

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Plan.objects.all()
        return Plan.objects.filter(is_active=True, service__is_active=True)
    
    @action(detail=True, methods=['get'])
    def features(self, request, pk=None):
        plan = self.get_object()
        return Response(plan.features)
    
    @action(detail=True, methods=['get'])
    def pricing(self, request, pk=None):
        plan = self.get_object()
        return Response({
            'price': plan.price,
            'duration': plan.duration,
            'features': plan.features,
        })

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsServiceOwner]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Subscription.objects.all()
        return Subscription.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        subscription = self.get_object()
        if subscription.is_active():
            return Response({
                'error': 'Subscription is already active'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        subscription.status = 'active'
        subscription.start_date = timezone.now()
        subscription.end_date = timezone.now() + timezone.timedelta(days=subscription.plan.duration)
        subscription.save()
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        if subscription.is_cancelled():
            return Response({
                'error': 'Subscription is already cancelled'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        subscription.status = 'cancelled'
        subscription.auto_renew = False
        subscription.save()
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk=None):
        subscription = self.get_object()
        new_plan_id = request.data.get('plan_id')
        
        try:
            new_plan = Plan.objects.get(id=new_plan_id)
            if new_plan.price <= subscription.plan.price:
                return Response({
                    'error': 'New plan must have a higher price'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            subscription.plan = new_plan
            subscription.save()
            
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Plan.DoesNotExist:
            return Response({
                'error': 'Plan not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def downgrade(self, request, pk=None):
        subscription = self.get_object()
        new_plan_id = request.data.get('plan_id')
        
        try:
            new_plan = Plan.objects.get(id=new_plan_id)
            if new_plan.price >= subscription.plan.price:
                return Response({
                    'error': 'New plan must have a lower price'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            subscription.plan = new_plan
            subscription.save()
            
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Plan.DoesNotExist:
            return Response({
                'error': 'Plan not found'
            }, status=status.HTTP_404_NOT_FOUND)

class ConfigViewSet(viewsets.ModelViewSet):
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer
    permission_classes = [permissions.IsAuthenticated, IsServiceAdmin]

class UsageViewSet(viewsets.ModelViewSet):
    serializer_class = UsageSerializer
    permission_classes = [permissions.IsAuthenticated, IsServiceOwner]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Usage.objects.all()
        return Usage.objects.filter(subscription__user=self.request.user)

class ServiceLogViewSet(viewsets.ModelViewSet):
    queryset = ServiceLog.objects.all()
    serializer_class = ServiceLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsServiceAdmin]

class ServiceMetricViewSet(viewsets.ModelViewSet):
    queryset = ServiceMetric.objects.all()
    serializer_class = ServiceMetricSerializer
    permission_classes = [permissions.IsAuthenticated, IsServiceAdmin]

class ServiceAlertViewSet(viewsets.ModelViewSet):
    queryset = ServiceAlert.objects.all()
    serializer_class = ServiceAlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsServiceAdmin]
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.resolve()
        serializer = self.get_serializer(alert)
        return Response(serializer.data) 