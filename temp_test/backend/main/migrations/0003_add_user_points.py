from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('main', '0002_add_points_redemption_rules'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='points',
            field=models.IntegerField(default=0, help_text='User points balance'),
        ),
    ] 