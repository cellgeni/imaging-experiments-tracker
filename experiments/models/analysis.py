from django.db import models

from experiments.models.measurement import Measurement, Channel


class SangerUser(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class SangerGroup(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Pipeline(models.Model):
    name = models.CharField(max_length=20, primary_key=True)


class PipelineVersion(models.Model):
    name = models.CharField(max_length=10)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)


class Registration(models.Model):
    measurements = models.ManyToManyField(Measurement)
    reference_channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)


class Stiching(models.Model):
    reference_channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)
    z = models.CharField(max_length=20)


class Microscope(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class ExternalUser(models.Model):
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(primary_key=True)

    def __str__(self):
        return self.email


class Analysis(models.Model):
    pipelineVersion = models.ForeignKey(PipelineVersion, on_delete=models.SET_NULL, null=True)
    microscope = models.ForeignKey(Microscope, on_delete=models.SET_NULL, null=True)
    registration = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True)
    stiching = models.ForeignKey(Stiching, on_delete=models.SET_NULL, null=True)
    # TODO: split in a separate one-to-one model
    OMERO_project = models.CharField(max_length=150, blank=True, null=True)
    OMERO_DATASET = models.CharField(max_length=150, blank=True, null=True)
    OMERO_internal_groups = models.ManyToManyField(SangerGroup)
    OMERO_internal_users = models.ManyToManyField(SangerUser)
    OMERO_external_users = models.ManyToManyField(ExternalUser)
