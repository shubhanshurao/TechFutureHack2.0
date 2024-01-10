# Generated by Django 4.2.2 on 2023-09-08 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0010_param_chart_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='status',
            field=models.CharField(choices=[('Unresolved', 'Unresolved'), ('Resolved', 'Resolved'), ('Acknowledged', 'Acknowledged')], default='Unresolved', max_length=50),
        ),
    ]