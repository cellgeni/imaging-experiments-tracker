from django.db import models
from django.utils import timezone

from experiments.models.measurement import Measurement, Channel
from experiments.models.base import NameModel


class SangerUser(NameModel):
    pass


class SangerGroup(NameModel):
    pass


class Pipeline(NameModel):
    pass


class PipelineVersion(models.Model):
    name = models.CharField(max_length=10)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pipeline) + self.name


class Registration(models.Model):
    measurements = models.ManyToManyField(Measurement)
    reference_channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.reference_channel)


class StichingZ(NameModel):
    pass


class Stiching(models.Model):
    reference_channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)
    z = models.ForeignKey(StichingZ, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.reference_channel} {self.z}"


class Microscope(NameModel):
    pass


class OmeroProject(NameModel):
    name = models.CharField(max_length=150)


class OmeroDataset(NameModel):
    name = models.CharField(max_length=150)


class ExternalUser(models.Model):
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(primary_key=True)

    def __str__(self):
        return self.email


class Status:
    REGISTERED = 0
    STARTED = 1
    FINISHED = 2
    FAILED = 3
    CHOICES = [
        (REGISTERED, 'Registered'),
        (STARTED, 'Started'),
        (FINISHED, 'Finished'),
        (FAILED, 'Failed'),
    ]


class Analysis(models.Model):
    pipelineVersion = models.ForeignKey(PipelineVersion, on_delete=models.SET_NULL, null=True)
    microscope = models.ForeignKey(Microscope, on_delete=models.SET_NULL, null=True)
    registration = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True)
    stichings = models.ManyToManyField(Stiching, blank=True)
    OMERO_project = models.ForeignKey(OmeroProject, on_delete=models.SET_NULL, null=True, blank=True)
    OMERO_DATASET = models.ForeignKey(OmeroDataset, on_delete=models.SET_NULL, null=True, blank=True)
    OMERO_internal_groups = models.ManyToManyField(SangerGroup)
    OMERO_internal_users = models.ManyToManyField(SangerUser)
    OMERO_external_users = models.ManyToManyField(ExternalUser)
    submitted_on = models.DateTimeField(default=timezone.now, null=True, blank=True)
    status = models.IntegerField(default=Status.REGISTERED, choices=Status.CHOICES, blank=True)

    def __str__(self):
        return f"{self.pk} {self.submitted_on}"
