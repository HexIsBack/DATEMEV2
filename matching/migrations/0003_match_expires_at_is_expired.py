from django.db import migrations, models
import django.utils.timezone
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('matching', '0002_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='match',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
    ]
