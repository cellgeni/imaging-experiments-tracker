# Generated by Django 3.0.2 on 2020-02-06 16:37

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CellGenProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ChannelTarget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.Channel')),
            ],
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.CellGenProject')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExternalUser',
            fields=[
                ('first_name', models.CharField(blank=True, max_length=30, null=True)),
                ('last_name', models.CharField(blank=True, max_length=30, null=True)),
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='LowMagReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MagBinOverlap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('automated_slide_id', models.CharField(blank=True, help_text="This is the ID entered into the Phenix when imaging. It should comprise the project code and then the slide ID from the BOND or a manual ID of the form ABXXXX where AB is the researcher's initials.", max_length=20, null=True)),
                ('automated_plate_id', models.CharField(blank=True, default=None, help_text='These columns are needed only when using the automated plate handler.', max_length=30, null=True)),
                ('automated_slide_num', models.CharField(blank=True, help_text='These columns are needed only when using the automated plate handler.', max_length=20, null=True)),
                ('image_cycle', models.IntegerField(help_text='Every time the coverslip is removed, the section restained with something, the image cycle increases incrementally')),
                ('date', models.DateField(default=datetime.date.today, help_text='Date that the image was taken')),
                ('notes_1', models.TextField(blank=True, help_text='Notes about the imaging process: what did you image (whole slide, part of tissue, single field), which channels?', max_length=200, null=True)),
                ('notes_2', models.TextField(blank=True, help_text='Notes about the resulting image: out of focus, poor signal in a channel, good, etc.', max_length=200, null=True)),
                ('export_location', models.CharField(blank=True, help_text='If the image dataset has been exported as a measurement via data management, this is the export location. This is NOT the same as basic image exports for presentations, lab notes, etc.', max_length=200, null=True)),
                ('archive_location', models.CharField(blank=True, help_text='If the image dataset has been exported as an archived measurement, this is the export location', max_length=200, null=True)),
                ('channel_target_pairs', models.ManyToManyField(help_text='Which channels are being used in imaging, and what targets do they represent? The channel name selected should exactly match the channels used on the Phenix.\t\t\t\t\t\t\t\t\t\t\t\t\t', to='experiments.ChannelTarget')),
                ('experiment', models.ForeignKey(blank=True, help_text='Pre-validated list of T283 projects', null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.Experiment')),
                ('low_mag_reference', models.ForeignKey(blank=True, help_text='A low magnification image (e.g. 5X or 10X scan of the whole slide with DAPI only) may be used as a reference for other images, in alignment and/or viewing. For other images, the related image number should be referenced.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.LowMagReference')),
                ('mag_bin_overlap', models.ForeignKey(blank=True, help_text='Magnification, binning level, and tile overlap for the image', null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.MagBinOverlap')),
            ],
        ),
        migrations.CreateModel(
            name='MeasurementNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Microscope',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OmeroDataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OmeroProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Researcher',
            fields=[
                ('first_name', models.CharField(blank=True, max_length=30, null=True)),
                ('last_name', models.CharField(blank=True, max_length=30, null=True)),
                ('employee_key', models.CharField(max_length=3, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('species', models.IntegerField(blank=True, choices=[(1, 'Hca'), (2, 'Mmu')], null=True)),
                ('age', models.CharField(blank=True, max_length=20, null=True)),
                ('genotype', models.CharField(blank=True, max_length=20, null=True)),
                ('background', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SangerGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SangerUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Slide',
            fields=[
                ('barcode_id', models.CharField(help_text='This is the slide number or ID assigned during sectioning', max_length=20, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='StichingZ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TeamDirectory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Technology',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tissue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='ZPlanes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Stiching',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_channel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.Channel')),
                ('z', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.StichingZ')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(help_text='In the case where there are multiple sections on the slide but only one imaged, which one? (1 = top, 2 = second from top… N = bottom)')),
                ('sample', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.Sample')),
                ('slide', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Slide')),
            ],
            options={
                'unique_together': {('number', 'slide', 'sample')},
            },
        ),
        migrations.AddField(
            model_name='sample',
            name='tissue',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.Tissue'),
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measurements', models.ManyToManyField(to='experiments.Measurement')),
                ('reference_channel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.Channel')),
            ],
        ),
        migrations.CreateModel(
            name='PipelineVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('pipeline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Pipeline')),
            ],
        ),
        migrations.AddField(
            model_name='measurement',
            name='measurement',
            field=models.ForeignKey(blank=True, help_text='Measurement number, assigned automatically by the Phenix', null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.MeasurementNumber'),
        ),
        migrations.AddField(
            model_name='measurement',
            name='researcher',
            field=models.ForeignKey(help_text='Pre-validated list of Phenix users', null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.Researcher'),
        ),
        migrations.AddField(
            model_name='measurement',
            name='sections',
            field=models.ManyToManyField(to='experiments.Section'),
        ),
        migrations.AddField(
            model_name='measurement',
            name='team_directory',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.TeamDirectory'),
        ),
        migrations.AddField(
            model_name='measurement',
            name='technology',
            field=models.ForeignKey(help_text='How was the slide stained?', null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.Technology'),
        ),
        migrations.AddField(
            model_name='measurement',
            name='z_planes',
            field=models.ForeignKey(blank=True, help_text='Number of z-planes x depth of each z-plane', null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.ZPlanes'),
        ),
        migrations.AddField(
            model_name='channeltarget',
            name='target',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.Target'),
        ),
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('OMERO_DATASET', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.OmeroDataset')),
                ('OMERO_external_users', models.ManyToManyField(to='experiments.ExternalUser')),
                ('OMERO_internal_groups', models.ManyToManyField(to='experiments.SangerGroup')),
                ('OMERO_internal_users', models.ManyToManyField(to='experiments.SangerUser')),
                ('OMERO_project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.OmeroProject')),
                ('microscope', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.Microscope')),
                ('pipelineVersion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.PipelineVersion')),
                ('registration', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.Registration')),
                ('stiching', models.ManyToManyField(blank=True, to='experiments.Stiching')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='channeltarget',
            unique_together={('channel', 'target')},
        ),
    ]
