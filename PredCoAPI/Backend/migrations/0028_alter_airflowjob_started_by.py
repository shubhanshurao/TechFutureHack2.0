# Generated by Django 4.2.2 on 2023-12-15 16:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Backend', '0027_watcher_conditions_watcher_params_watcher_thresholds_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='airflowjob',
            name='Started_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
