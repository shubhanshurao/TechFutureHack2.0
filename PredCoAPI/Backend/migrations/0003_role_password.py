# Generated by Django 4.1.4 on 2023-07-31 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0002_remove_param_type_param_datatype'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='password',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
