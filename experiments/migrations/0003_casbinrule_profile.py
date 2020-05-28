# Generated by Django 3.0.6 on 2020-05-28 11:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('experiments', '0002_fix_verbose_names'),
    ]

    operations = [
        migrations.CreateModel(
            name='CasbinRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ptype', models.CharField(blank=True, max_length=255, null=True)),
                ('username', models.CharField(blank=True, db_column='v0', max_length=255, null=True)),
                ('obj_type', models.CharField(blank=True, db_column='v1', max_length=255, null=True)),
                ('obj_id', models.CharField(blank=True, db_column='v2', max_length=255, null=True)),
                ('action', models.CharField(blank=True, db_column='v3', max_length=255, null=True)),
                ('v4', models.CharField(blank=True, max_length=255, null=True)),
                ('v5', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'casbin_rule',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_external', models.BooleanField(default=False, verbose_name='External group member')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
