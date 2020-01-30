import uuid
from datetime import date
from typing import Tuple

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from experiments.models.sample import Sample


class CellGenProject(models.Model):
    key = models.CharField(max_length=20)

    def __str__(self):
        return self.key


class TeamDirectory(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Technology(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Researcher(models.Model):
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    employee_key = models.CharField(max_length=3, primary_key=True)

    def __str__(self):
        return self.employee_key


class Slide(models.Model):
    barcode_id = models.CharField(max_length=20, primary_key=True, help_text="This is the slide number "
                                                                             "or ID assigned during sectioning")
    automated_id = models.CharField(max_length=20, help_text="This is the ID entered into the Phenix when imaging. "
                                                             "It should comprise the project code and then the slide ID "
                                                             "from the BOND or a manual ID of the form ABXXXX "
                                                             "where AB is the researcher's initials.")

    def __str__(self):
        return self.barcode_id

    @classmethod
    def get_random_slide_with_three_sections(cls) -> "Slide":
        for slide in cls.objects.all():
            if len(slide.section_set.all()) >= 3:
                return slide

    @classmethod
    def get_slide(cls, barcode_id):
        try:
            return Slide.objects.get(barcode_id=barcode_id)
        except ObjectDoesNotExist:
            raise ValueError(f"Slide with barcode {barcode_id} does not exist")


class Section(models.Model):
    class Meta:
        unique_together = (('number', 'slide'),)

    number = models.IntegerField(help_text="In the case where there are multiple sections on the slide "
                                           "but only one imaged, which one? (1 = top, 2 = second from top… N = bottom)")
    sample = models.ForeignKey(Sample, on_delete=models.SET_NULL, null=True)
    slide = models.ForeignKey(Slide, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.number} {self.sample} {self.slide}"

    @classmethod
    def get_section(cls, num, slide):
        try:
            return cls.objects.get(number=num,
                                   slide=slide)
        except ObjectDoesNotExist:
            raise ValueError(f"Section number {num} does not exist for slide {slide}")


class Channel(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Target(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class ChannelTarget(models.Model):
    SEPARATOR = " -> "

    class Meta:
        unique_together = ("channel", "target")

    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)
    target = models.ForeignKey(Target, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.channel) + self.SEPARATOR + str(self.target)

    @classmethod
    def get_channel_and_target_from_str(cls, name: str) -> Tuple[str, str]:
        if type(name) is not str or cls.SEPARATOR not in name:
            raise ValueError(f"The string '{str}' is not a ChannelTarget string")
        channel, target = name.split(cls.SEPARATOR)
        return channel, target


class Experiment(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    project = models.ForeignKey(CellGenProject, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class MeasurementNumber(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class LowMagReference(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class MagBinOverlap(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class ZPlanes(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Measurement(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    sections = models.ManyToManyField(Section)
    researcher = models.ForeignKey(Researcher, on_delete=models.SET_NULL, null=True,
                                   help_text="Pre-validated list of Phenix users")
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True, blank=True,
                                   help_text="Pre-validated list of T283 projects")
    technology = models.ForeignKey(Technology, on_delete=models.SET_NULL, null=True,
                                   help_text="How was the slide stained?")
    automated_plate_id = models.CharField(max_length=20, null=True, default=None, blank=True,
                                          help_text="These columns are needed only "
                                                    "when using the automated plate handler.")
    automated_slide_num = models.CharField(max_length=10, blank=True, null=True,
                                           help_text="These columns are needed only "
                                                     "when using the automated plate handler.")
    image_cycle = models.IntegerField(help_text="Every time the coverslip is removed, "
                                                "the section restained with something, "
                                                "the image cycle increases incrementally")
    channel_target_pairs = models.ManyToManyField(ChannelTarget,
                                                  help_text="Which channels are being used in imaging, "
                                                            "and what targets do they represent? The channel name "
                                                            "selected should exactly match "
                                                            "the channels used on the Phenix.													")
    date = models.DateField(default=date.today,
                            help_text="Date that the image was taken")
    measurement = models.ForeignKey(MeasurementNumber, on_delete=models.SET_NULL, null=True, blank=True,
                                   help_text="Measurement number, assigned automatically by the Phenix")
    low_mag_reference = models.ForeignKey(LowMagReference, on_delete=models.SET_NULL, blank=True, null=True,
                                         help_text="A low magnification image (e.g. 5X or 10X scan "
                                                   "of the whole slide with DAPI only) may be used as a reference "
                                                   "for other images, in alignment and/or viewing. For other images, "
                                                   "the related image number should be referenced.")
    mag_bin_overlap = models.ForeignKey(MagBinOverlap, models.SET_NULL, blank=True, null=True,
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
    export_location = models.CharField(max_length=200, blank=True, null=True,
                                       help_text="If the image dataset has been exported as a measurement "
                                                 "via data management, this is the export location. "
                                                 "This is NOT the same as basic image exports "
                                                 "for presentations, lab notes, etc.")
    archive_location = models.CharField(max_length=200, blank=True, null=True,
                                        help_text="If the image dataset has been exported as an archived measurement, "
                                                  "this is the export location")
    team_directory = models.ForeignKey(TeamDirectory, on_delete=models.SET_NULL, null=True)

    DATE_FORMAT = "%d.%m.%Y"

    def __str__(self):
        return f"{self.sections} {self.date} {self.measurement}"
