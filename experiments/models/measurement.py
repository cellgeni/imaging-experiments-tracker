from datetime import date

from django.db import models
from django.utils import timezone
from django.dispatch import receiver

from experiments.constants import *
from experiments.models.base import NameModel, Path


class Project(NameModel):
    pass


class Plate(NameModel):
    pass


class Technology(NameModel):
    class Meta:
        verbose_name_plural = "Technologies"


class Researcher(models.Model):
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    login = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return self.login


class Channel(NameModel):
    pass


class Target(NameModel):
    pass


class ChannelTarget(models.Model):
    SEPARATOR = " -> "

    class Meta:
        unique_together = ("channel", "target")

    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)
    target = models.ForeignKey(Target, on_delete=models.SET_NULL, null=True)

    @classmethod
    def create_channel_target(cls, channel_name: str, target_name: str) -> 'ChannelTarget':
        """Create ChannelTarget object from channel name and target name."""
        channel = Channel.objects.get(name=channel_name)
        target = Target.objects.get_or_create(name=target_name)[0]
        return cls.objects.get_or_create(channel=channel, target=target)[0]

    def __str__(self):
        return str(self.channel) + self.SEPARATOR + str(self.target)


class Experiment(NameModel):
    pass


class MeasurementNumber(NameModel):
    pass


class LowMagReference(NameModel):
    pass


class MagBinOverlap(NameModel):
    pass


class ZPlanes(NameModel):
    class Meta:
        verbose_name_plural = "ZPlanes"


class TeamDirectory(NameModel):
    class Meta:
        verbose_name_plural = "TeamDirectories"


class ExportLocation(Path):
    pass


class ArchiveLocation(Path):
    pass


class Measurement(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['plate',
                                            'measurement_number', 'date'], name="unique_measurement"),
        ]

    researcher = models.ForeignKey(Researcher, on_delete=models.SET_NULL, null=True,
                                   help_text="Pre-validated list of Phenix users")
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                help_text="Pre-validated list of T283 projects")
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, null=True, blank=True,
                                   help_text="Pre-validated list of T283 projects")
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE,
                                   help_text="How was the slide stained?")
    plate = models.ForeignKey(Plate, null=True, blank=True, on_delete=models.SET_NULL,
                              help_text="A plate name given by automated microscopy system "
                                        "when imaged automatically")
    image_cycle = models.IntegerField(help_text="Every time the coverslip is removed, "
                                                "the section restained with something, "
                                                "the image cycle increases incrementally")
    channel_target_pairs = models.ManyToManyField(ChannelTarget,
                                                  help_text="Which channels are being used in imaging, "
                                                            "and what targets do they represent? The channel name "
                                                            "selected should exactly match "
                                                            "the channels used on the Phenix.")
    date = models.DateField(default=date.today,
                            help_text="Date that the image was taken")
    measurement_number = models.ForeignKey(MeasurementNumber, on_delete=models.CASCADE,
                                           help_text="Measurement number assigned automatically by the Phenix")
    low_mag_reference = models.ForeignKey(LowMagReference, on_delete=models.SET_NULL, null=True,
                                          help_text="A low magnification image (e.g. 5X or 10X scan "
                                                    "of the whole slide with DAPI only) may be used as a reference "
                                                    "for other images, in alignment and/or viewing. For other images, "
                                                    "the related image number should be referenced.")
    mag_bin_overlap = models.ForeignKey(MagBinOverlap, models.SET_NULL, null=True,
                                        help_text="Magnification, binning level, and tile overlap for the image")
    z_planes = models.ForeignKey(ZPlanes, on_delete=models.SET_NULL, blank=True, null=True,
                                 help_text="Number of z-planes x depth of each z-plane")
    notes_1 = models.TextField(max_length=200, blank=True, null=True,
                               help_text="Notes about the imaging process: "
                                         "what did you image (whole slide, part of tissue, single field), "
                                         "which channels?")
    notes_2 = models.TextField(max_length=200, blank=True, null=True,
                               help_text="Notes about the resulting image: "
                                         "out of focus, poor signal in a channel, good, etc.")
    post_stain = models.TextField(max_length=200, blank=True, null=True,
                                  help_text="Notes about additional chemical treatments used "
                                            "to improve imaging without changing the targets or fluorophores.")
    harmony_copy_deleted = models.BooleanField(default=False, blank=True)
    export_location = models.ForeignKey(ExportLocation, blank=True, null=True, on_delete=models.SET_NULL,
                                        help_text="Folder with the resulting image")
    archive_location = models.ForeignKey(ArchiveLocation, blank=True, null=True, on_delete=models.SET_NULL,
                                         help_text="Folder with the resulting image if archived")
    team_directory = models.ForeignKey(TeamDirectory, on_delete=models.SET_NULL, null=True, blank=True)
    imported_on = models.DateTimeField(default=timezone.now, editable=False)

    VALIDATION_NEEDED = {RESEARCHER, PROJECT, SPECIES, TECHNOLOGY, CHANNEL}

    def __str__(self):
        return f"{self.id} {self.date}"

    def has_slide_number(self, slide_number: int) -> bool:
        """Return True if measurement has this automated_slide_num among its slots."""
        return slide_number in {slot.automated_slide_num for slot in self.slot_set.all()}

    def copy_non_core_attributes(self, new: 'Measurement') -> None:
        """Copy attributes that do not make a measurement unique from a new measurement"""
        self.researcher = new.researcher
        self.image_cycle = new.image_cycle
        self.mag_bin_overlap = new.mag_bin_overlap
        self.project = new.project
        self.technology = new.technology
        self.low_mag_reference = new.low_mag_reference
        self.z_planes = new.z_planes
        self.notes_1 = new.notes_1
        self.notes_2 = new.notes_2
        self.export_location = new.export_location
        self.archive_location = new.archive_location
        self.team_directory = new.team_directory
        self.harmony_copy_deleted = new.harmony_copy_deleted
        self.post_stain = new.post_stain
        self.save()
