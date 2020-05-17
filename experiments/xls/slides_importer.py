from typing import Union, List

from django.db import models

from experiments.constants import *
from experiments.helpers import is_empty
from experiments.models import Sample, SlideBarcode
from experiments.models.slide import Slide, Section
from experiments.xls import xls_logger as logger, MODELS_MAPPING, EntitiesImporter


class SamplesImporter(EntitiesImporter):
    """
    Imports samples from a given row
    """

    def get_or_create_sample_property(self, column: str, suffix: str) -> Union[models.Model, None]:
        """
        Create an instance of an attribute of a sample (e.g. age, genotype, background) with value from `column` + `suffix`
        :param column: defines a type of entity that will be created, must be one of the
                spreadsheet column names
        :param suffix: underscore with number, helps to locate the exact column
        :return: an instance of the model that was created
        e.g. column == 'Tissue', suffix==`_1` an instance of a model Tissue
        with value from column 'Tissue_1` will be returned
        """
        value = self.row.get(column + suffix)
        return MODELS_MAPPING[column](value) if not is_empty(value) else None

    def import_samples(self) -> None:
        """Import all samples in a row."""
        for s_column in SAMPLES:
            sample_name = self.row.get(s_column)
            if sample_name:
                self.import_sample(sample_name, s_column)

    def import_sample(self, sample_name, s_column: str) -> None:
        """Import a sample from a row given a column name."""
        suffix = s_column[-2:]
        tissue = self.get_or_create_sample_property(TISSUE, suffix)
        background = self.get_or_create_sample_property(BACKGROUND, suffix)
        genotype = self.get_or_create_sample_property(GENOTYPE, suffix)
        age = self.get_or_create_sample_property(AGE, suffix)
        sample = Sample.objects.get_or_create(name=sample_name)[0]
        sample.tissue = tissue
        sample.age = age
        sample.background = background
        sample.genotype = genotype
        sample.save()


class SlidesImporter(EntitiesImporter):

    def __init__(self, row):
        super().__init__(row)
        self.sample_ids = self.get_sample_ids()

    def get_sample_ids(self) -> List[str]:
        """Return a list of sample ids from this row"""
        sample_ids = []
        for s_column in SAMPLES:
            s_id = self.row.get(s_column)
            if s_id:
                sample_ids.append(s_id)
        return sample_ids

    def import_sections(self, slide: Slide) -> None:
        """Create slots from a row and attach them to a given slide."""
        for number, sample_id in enumerate(self.sample_ids):
            if sample_id:
                sample = Sample.objects.get_or_create(name=sample_id)[0]
                Section.objects.update_or_create(number=number + 1, sample=sample, slide=slide)

    def import_slide(self) -> Slide:
        """Create barcodes, slides and slots from a row."""
        try:
            barcode = SlideBarcode.objects.get_or_create(name=self.row[SLIDE_BARCODE])[0]
            slides = Slide.objects.filter(barcode=barcode)
            # TODO: refactor
            for slide in slides:
                if slide.contains_all_samples(self.sample_ids):
                    return slide
            slide = Slide.objects.create(barcode=barcode)
            self.import_sections(slide)
            return slide
        except KeyError as e:
            logger.error(f"Slide barcode absent")
