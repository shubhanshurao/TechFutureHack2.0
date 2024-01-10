# Generated by Django 4.2.2 on 2023-09-16 10:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Backend', '0015_airflowjob'),
    ]

    operations = [
        migrations.AddField(
            model_name='airflowjob',
            name='File_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='airflowjob',
            name='Started_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]