from django.db import models
from django.utils import timezone


class CellGenProject(models.Model):
    key = models.CharField(max_length=4)

    def __str__(self):
        return self.key


class TeamDirectory(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Researcher(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    employee_key = models.CharField(max_length=3, primary_key=True)

    def __str__(self):
        return self.employee_key


class Sample(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    species = models.CharField(max_length=20, choices=())
    age = models.CharField(max_length=20)
    genotype = models.CharField(max_length=20, null=True)
    background = models.CharField(max_length=20, null=True)
    tissue = models.CharField(max_length=20)

    def __str__(self):
        return self.id


class Slide(models.Model):
    automated_id = models.CharField(max_length=20)
    barcode_id = models.CharField(max_length=20, primary_key=True)

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
    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)
    target = models.ForeignKey(Target, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.channel) + " -> " + str(self.target)


class Experiment(models.Model):
    name = models.CharField(max_length=20)
    project = models.ForeignKey(CellGenProject, on_delete=models.SET_NULL, null=True)
    team_directory = models.ForeignKey(TeamDirectory, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Measurement(models.Model):
    slide = models.ForeignKey(Slide, on_delete=models.SET_NULL, null=True)
    researcher = models.ForeignKey(Researcher, on_delete=models.SET_NULL, null=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True)
    technology = models.CharField(max_length=20)
    automated_plate_id = models.CharField(max_length=20, null=True, default=None, blank=True)
    automated_slide_num = models.IntegerField(null=True)
    image_cycle = models.IntegerField()
    channel_target_pairs = models.ManyToManyField(ChannelTarget)
    date = models.DateTimeField(default=timezone.now)
    measurement = models.CharField(max_length=20)
    low_mag_reference = models.CharField(max_length=20)
    mag_bin_overlap = models.CharField(max_length=20)
    z_planes = models.CharField(max_length=20)
    microscope = models.CharField(max_length=20, choices=(("phenix", "Phenix"),
                                                          ('plateloader', 'Phenix Plateloader')))
    notes_1 = models.TextField(max_length=200)
    notes_2 = models.TextField(max_length=200)

    def __str__(self):
        return f"{self.slide} {self.date} {self.measurement}"


class Pipeline(models.Model):
    name = models.CharField(max_length=20, primary_key=True)


class PipelineVersion(models.Model):
    name = models.CharField(max_length=10)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)


class Analysis(models.Model):
    pipelineVersion = models.ForeignKey(PipelineVersion, on_delete=models.SET_NULL, null=True)
