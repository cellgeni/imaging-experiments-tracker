# Generated by Django 3.0.2 on 2020-01-29 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0002_auto_20200129_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measurement',
            name='automated_slide_num',
            field=models.CharField(blank=True, help_text='These columns are needed only when using the automated plate handler.', max_length=10, null=True),
        ),
    ]
