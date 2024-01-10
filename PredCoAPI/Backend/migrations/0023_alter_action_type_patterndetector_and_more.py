# Generated by Django 4.2.2 on 2023-10-29 18:24

import Backend.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0022_organization_certificatearn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='Type',
            field=models.CharField(choices=[('Watcher', 'Watcher'), ('Anomaly', 'Anomaly'), ('Geofence', 'Geofence'), ('Device', 'Device')], default='Watcher', max_length=50),
        ),
        migrations.CreateModel(
            name='PatternDetector',
            fields=[
                ('ID', models.SlugField(default=Backend.models.custom_id, editable=False, max_length=40, primary_key=True, serialize=False)),
                ('Patterns', models.CharField(max_length=500, null=True)),
                ('Param', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Backend.param')),
            ],
        ),
        migrations.CreateModel(
            name='DetectedPatternAlert',
            fields=[
                ('ID', models.SlugField(default=Backend.models.custom_id, editable=False, max_length=40, primary_key=True, serialize=False)),
                ('Name', models.CharField(max_length=200, null=True)),
                ('Param_detected_in', models.CharField(max_length=50, null=True)),
                ('Detected_pattern', models.CharField(max_length=50, null=True)),
                ('Status', models.CharField(choices=[('Closed', 'Closed'), ('Canceled', 'Canceled'), ('Acknowledged', 'Acknowledged'), ('New', 'New')], default='New', max_length=50, null=True)),
                ('Created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('Device', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Backend.device')),
            ],
        ),
    ]