# Generated by Django 3.0.8 on 2020-08-01 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0005_auto_20200801_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobilenumber',
            name='number',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
