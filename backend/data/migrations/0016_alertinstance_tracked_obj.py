# Generated by Django 3.0.8 on 2020-08-03 02:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0015_remove_alert_alert_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='alertinstance',
            name='tracked_obj',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='data.TrackedObject'),
        ),
    ]
