from django.db import models

from experiments.models.base import NameModel
from experiments.models.measurement import Measurement, MeasurementNumber
from experiments.models.slide import Section


class AutomatedSlide(NameModel):
    """Really this model should be called 'AutomatedSlide' but I decided to keep it this way to prevent
    mental converting every time someone stumbles on AUTOMATED_SLIDE_ID in a spreadsheet"""
    pass


class Slot(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['measurement', 'automated_slide_num'], name="unique_slide_num"),
        ]

    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE,
                                    help_text="A measurement_number to which a slot on a given plate corresponds")
    automated_slide = models.ForeignKey(AutomatedSlide, on_delete=models.CASCADE,
                                        help_text="A slide ID given to a slot on a given plate")
    automated_slide_num = models.IntegerField(help_text="Number of a slot on a plate, for Phoenix it's from 1 to 4",
                                              null=True, blank=True)
    sections = models.ManyToManyField(Section)
