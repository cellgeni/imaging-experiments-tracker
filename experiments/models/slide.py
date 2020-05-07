from typing import List

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from experiments.models import Sample, NameModel


class SlideBarcode(NameModel):
    pass


class Slide(models.Model):
    barcode = models.ForeignKey(SlideBarcode, on_delete=models.CASCADE,
                                help_text="Barcode ID printed on a physical slide")

    def __str__(self):
        return f"{self.id}, Barcode: {self.barcode}"

    def contains_all_samples(self, sample_ids: List[str]) -> bool:
        """Check whether a slide instance has slots with given samples."""
        return set({section.sample.name for section in self.section_set.all()}) == set(sample_ids)


class Section(models.Model):
    class Meta:
        unique_together = (('number', 'slide'),)

    number = models.IntegerField(help_text="Section number on a slide: 1 = top, 2 = second from top… N = bottom)")
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
