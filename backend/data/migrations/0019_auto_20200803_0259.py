# Generated by Django 3.0.8 on 2020-08-03 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0018_alertnotification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='alert_type',
            field=models.CharField(default='new record', max_length=100),
        ),
    ]