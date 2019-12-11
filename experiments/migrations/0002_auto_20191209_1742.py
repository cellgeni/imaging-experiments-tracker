# Generated by Django 3.0 on 2019-12-09 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='section',
            name='number',
            field=models.IntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='section',
            unique_together={('number', 'slide')},
        ),
    ]
