from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('main', '0003_add_user_points'),
    ]

    operations = [
        migrations.CreateModel(
            name='PointsTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('earn', 'Earned'), ('spend', 'Spent'), ('system', 'System')], max_length=10)),
                ('points', models.IntegerField()),
                ('description', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points_transactions', to='main.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ] 