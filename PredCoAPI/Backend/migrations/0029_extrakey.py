# Generated by Django 4.2.2 on 2023-12-17 10:44

import Backend.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0028_alter_airflowjob_started_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtraKey',
            fields=[
                ('ID', models.SlugField(default=Backend.models.custom_id, editable=False, max_length=40, primary_key=True, serialize=False)),
                ('Model_type', models.CharField(max_length=255, null=True)),
                ('Model_id', models.CharField(max_length=255, null=True)),
                ('Key_type', models.CharField(max_length=255, null=True)),
                ('Key_value', models.TextField(null=True)),
            ],
        ),
    ]
