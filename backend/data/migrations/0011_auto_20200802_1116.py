# Generated by Django 3.0.8 on 2020-08-02 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0010_auto_20200802_0947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ipdr',
            name='download_data_volume',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='ipdr',
            name='upload_data_volume',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True),
        ),
    ]
