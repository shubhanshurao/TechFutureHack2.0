# Generated by Django 4.2.2 on 2023-12-20 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0031_alter_mlmodel_column_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='Push_Notifications',
            field=models.BooleanField(default=True),
        ),
    ]
