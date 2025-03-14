from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
import secrets
from rest_framework import serializers

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_points_balance(request):
    """Get user's points balance."""
    return Response({
        'points': request.user.points
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_points_history(request):
    """Get user's points transaction history."""
    transactions = request.user.get_points_history()
    serializer = PointsTransactionSerializer(transactions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_redemption_rules(request):
    """Get available points redemption rules."""
    rules = PointsRedemptionRule.objects.filter(is_active=True)
    serializer = PointsRedemptionRuleSerializer(rules, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def redeem_points(request):
    """Redeem points for a reward."""
    rule_id = request.data.get('rule_id')
    
    try:
        rule = PointsRedemptionRule.objects.get(id=rule_id, is_active=True)
        
        # Check if user has enough points
        if request.user.points < rule.points_required:
            return Response({
                'error': 'Insufficient points'
            }, status=400)
        
        # Check if user has an active subscription
        active_subscription = Subscription.objects.filter(
            user=request.user,
            is_active=True,
            expiry_date__gt=timezone.now()
        ).first()
        
        if not active_subscription:
            return Response({
                'error': 'No active subscription found'
            }, status=400)
        
        # Apply the reward
        with transaction.atomic():
            # Deduct points
            request.user.points -= rule.points_required
            request.user.save()
            
            # Create points transaction
            PointsTransaction.objects.create(
                user=request.user,
                type="spend",
                points=rule.points_required,
                description=f"Redeemed for {rule.name}"
            )
            
            # Apply the reward based on rule type
            if rule.reward_type == "discount":
                # Create discount code
                discount_code = secrets.token_urlsafe(8)
                Discount.objects.create(
                    code=discount_code,
                    percentage=rule.reward_value,
                    expiry_date=timezone.now() + timezone.timedelta(days=7)
                )
                reward_text = f"Discount code: {discount_code}"
            elif rule.reward_type == "days":
                # Extend subscription
                active_subscription.expiry_date += timezone.timedelta(days=rule.reward_value)
                active_subscription.save()
                reward_text = f"{rule.reward_value} days extension"
            else:
                reward_text = rule.name
        
        return Response({
            'success': True,
            'points_spent': rule.points_required,
            'reward': reward_text,
            'new_balance': request.user.points
        })
        
    except PointsRedemptionRule.DoesNotExist:
        return Response({
            'error': 'Invalid redemption rule'
        }, status=400)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

# Add points-related serializers
class PointsTransactionSerializer(serializers.ModelSerializer):
    """Serializer for points transactions."""
    class Meta:
        model = PointsTransaction
        fields = ('id', 'type', 'points', 'description', 'created_at')

class PointsRedemptionRuleSerializer(serializers.ModelSerializer):
    """Serializer for points redemption rules."""
    class Meta:
        model = PointsRedemptionRule
        fields = ('id', 'name', 'description', 'points_required', 'reward_type', 'reward_value') 