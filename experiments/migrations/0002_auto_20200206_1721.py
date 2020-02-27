# Generated by Django 3.0.2 on 2020-02-06 17:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='analysis',
            old_name='stiching',
            new_name='stichings',
        ),
        migrations.AddField(
            model_name='analysis',
            name='submitted_on',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
