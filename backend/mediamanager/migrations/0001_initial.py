# Generated by Django 3.0.8 on 2020-08-01 04:28

from django.db import migrations, models
import mediamanager.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MediaManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', help_text='Media file title', max_length=2000)),
                ('type', models.CharField(choices=[('sheet', 'sheet')], default='sheet', max_length=255)),
                ('media_file', models.FileField(help_text='Upload media file', max_length=2000, upload_to=mediamanager.models.upload_handler)),
                ('url', models.URLField(blank=True, help_text='Media url will be populated after uploading file.', null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
