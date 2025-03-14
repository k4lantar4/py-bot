from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_create_points_transaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='PointsRedemptionRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('points_required', models.IntegerField()),
                ('reward_type', models.CharField(choices=[('discount', 'Discount Code'), ('days', 'Subscription Days'), ('other', 'Other')], max_length=20)),
                ('reward_value', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PointsRedemption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points_spent', models.IntegerField()),
                ('reward_value', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.pointsredemptionrule')),
                ('subscription', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.subscription')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ] 