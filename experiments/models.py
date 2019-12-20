from django.db import models
from django.utils import timezone


class CellGenProject(models.Model):
    key = models.CharField(max_length=20    )

    def __str__(self):
        return self.key


class TeamDirectory(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Microscope(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Technology(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class SangerUser(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class SangerGroup(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Researcher(models.Model):
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    employee_key = models.CharField(max_length=3, primary_key=True)

    def __str__(self):
        return self.employee_key


class ExternalUser(models.Model):
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(primary_key=True)

    def __str__(self):
        return self.email


class Tissue(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Sample(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    species = models.CharField(max_length=20, choices=())
    age = models.CharField(max_length=20)
    genotype = models.CharField(max_length=20, null=True)
    background = models.CharField(max_length=20, null=True)
    tissue = models.ForeignKey(Tissue, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.id


class Slide(models.Model):
    barcode_id = models.CharField(max_length=20, primary_key=True, help_text="An ID of a physical slide")
    automated_id = models.CharField(max_length=20, help_text="An ID assigned to a slide by a microscope")

    def __str__(self):
        return self.barcode_id


class Section(models.Model):

    class Meta:
        unique_together = (('number', 'slide'),)

    number = models.IntegerField()
    sample = models.ForeignKey(Sample, on_delete=models.SET_NULL, null=True)
    slide = models.ForeignKey(Slide, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.number} {self.sample} {self.slide}"


class Channel(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Target(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class ChannelTarget(models.Model):

    class Meta:
        unique_together = ("channel", "target")

    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)
    target = models.ForeignKey(Target, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.channel) + " -> " + str(self.target)


class Experiment(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    project = models.ForeignKey(CellGenProject, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Measurement(models.Model):
    sections = models.ManyToManyField(Section)
    researcher = models.ForeignKey(Researcher, on_delete=models.SET_NULL, null=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True)
    technology = models.ForeignKey(Technology, on_delete=models.SET_NULL, null=True)
    automated_plate_id = models.CharField(max_length=20, null=True, default=None, blank=True)
    automated_slide_num = models.IntegerField(blank=True, null=True)
    image_cycle = models.IntegerField()
    channel_target_pairs = models.ManyToManyField(ChannelTarget)
    date = models.DateTimeField(default=timezone.now)
    measurement = models.CharField(max_length=20)
    low_mag_reference = models.CharField(max_length=20, blank=True, null=True)
    mag_bin_overlap = models.CharField(max_length=20, blank=True, null=True)
    z_planes = models.CharField(max_length=20, blank=True, null=True)
    notes_1 = models.TextField(max_length=200, blank=True, null=True)
    notes_2 = models.TextField(max_length=200, blank=True, null=True)
    export_location = models.CharField(max_length=200, blank=True, null=True)
    archive_location = models.CharField(max_length=200, blank=True, null=True)
    team_directory = models.ForeignKey(TeamDirectory, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.sections} {self.date} {self.measurement}"


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

