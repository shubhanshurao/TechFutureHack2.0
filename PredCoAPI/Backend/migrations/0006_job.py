# Generated by Django 4.2.2 on 2023-08-22 06:00

import Backend.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0005_alert_breached_condition_alert_breached_param_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('ID', models.SlugField(default=Backend.models.custom_id, editable=False, max_length=40, primary_key=True, serialize=False)),
                ('Name', models.CharField(max_length=150, null=True)),
                ('Type', models.CharField(choices=[('Anomaly Detection', 'Anomaly Detection')], default='Anomaly Detection', max_length=50)),
                ('Api_key_hash', models.CharField(default=Backend.models.keygenerator, editable=False, max_length=50, null=True)),
                ('Job_id', models.CharField(max_length=250, null=True)),
                ('Active', models.BooleanField(default=False)),
                ('Created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True, null=True)),
                ('Device', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Backend.device')),
            ],
        ),
    ]
