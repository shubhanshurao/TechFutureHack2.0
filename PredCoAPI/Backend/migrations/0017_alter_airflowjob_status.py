# Generated by Django 4.2.2 on 2023-09-17 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0016_airflowjob_file_name_airflowjob_started_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='airflowjob',
            name='Status',
            field=models.CharField(choices=[('In Progress....', 'In Progress....'), ('Completed', 'Completed'), ('Failed', 'Failed')], default='In Progress....', max_length=50),
        ),
    ]