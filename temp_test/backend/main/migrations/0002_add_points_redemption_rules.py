from django.db import migrations

def create_redemption_rules(apps, schema_editor):
    PointsRedemptionRule = apps.get_model('main', 'PointsRedemptionRule')
    
    # VIP Status Rule
    PointsRedemptionRule.objects.create(
        name="VIP Status (1 Month)",
        description="Get VIP status for 1 month with exclusive benefits",
        points_cost=1000,
        reward_type="vip",
        reward_value=1,
        is_active=True
    )
    
    # Extra Data Rules
    PointsRedemptionRule.objects.create(
        name="Extra 10GB Data",
        description="Add 10GB to your active subscription",
        points_cost=500,
        reward_type="data",
        reward_value=10,
        is_active=True
    )
    
    PointsRedemptionRule.objects.create(
        name="Extra 50GB Data",
        description="Add 50GB to your active subscription",
        points_cost=2000,
        reward_type="data",
        reward_value=50,
        is_active=True
    )
    
    # Extra Days Rules
    PointsRedemptionRule.objects.create(
        name="Extra 7 Days",
        description="Extend your subscription by 7 days",
        points_cost=300,
        reward_type="days",
        reward_value=7,
        is_active=True
    )
    
    PointsRedemptionRule.objects.create(
        name="Extra 30 Days",
        description="Extend your subscription by 30 days",
        points_cost=1000,
        reward_type="days",
        reward_value=30,
        is_active=True
    )
    
    # Discount Rules
    PointsRedemptionRule.objects.create(
        name="10% Discount",
        description="Get a 10% discount on your next purchase",
        points_cost=500,
        reward_type="discount",
        reward_value=10,
        is_active=True
    )
    
    PointsRedemptionRule.objects.create(
        name="25% Discount",
        description="Get a 25% discount on your next purchase",
        points_cost=1000,
        reward_type="discount",
        reward_value=25,
        is_active=True
    )

def remove_redemption_rules(apps, schema_editor):
    PointsRedemptionRule = apps.get_model('main', 'PointsRedemptionRule')
    PointsRedemptionRule.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_redemption_rules, remove_redemption_rules),
    ] 