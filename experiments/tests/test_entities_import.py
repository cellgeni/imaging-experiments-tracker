from django.test import TestCase

from experiments.models import *
from experiments.xls.slides_importer import SamplesImporter, SlidesImporter
from experiments import RowT
from experiments.models.slide import Slide


class SamplesImportTestCase(TestCase):

    @staticmethod
    def get_sample_row() -> RowT:
        return {
            TISSUE1: "Kidney (normal)",
            SAMPLE1: "L14-KID-0-FFPE-2-S4",
            TISSUE2: "HEART",
            SAMPLE2: "id",
            AGE2: "unknown",
            BACKGROUND2: "known",
            GENOTYPE2: "unbeknown",
            TISSUE3: "LEG",
            SAMPLE3: "id2",
            AGE3: "fetal",
            SAMPLE4: "id5",
            AGE4: "baby",
        }

    def _test_tissue(self, samplesImporter: SamplesImporter, suffix: str, sample: Sample):
        self.assertEqual(sample.tissue, samplesImporter.get_or_create_sample_property(TISSUE, suffix))

    def _test_age(self, samplesImporter: SamplesImporter, suffix: str, sample: Sample):
        self.assertEqual(sample.age, samplesImporter.get_or_create_sample_property(AGE, suffix))

    def _test_genotype(self, samplesImporter: SamplesImporter, suffix: str, sample: Sample):
        self.assertEqual(sample.genotype, samplesImporter.get_or_create_sample_property(GENOTYPE, suffix))

    def _test_background(self, samplesImporter: SamplesImporter, suffix: str, sample: Sample):
        self.assertEqual(sample.background, samplesImporter.get_or_create_sample_property(BACKGROUND, suffix))

    def test_import_samples(self):
        row = self.get_sample_row()
        si = SamplesImporter(row)
        si.import_samples()
        for s_column in SAMPLES:
            s = row.get(s_column)
            if s:
                sample = Sample.objects.get(name=s)
                suffix = s_column[-2:]
                self._test_tissue(si, suffix, sample)
                self._test_age(si, suffix, sample)
                self._test_background(si, suffix, sample)
                self._test_genotype(si, suffix, sample)


class SlidesImportTestCase(TestCase):
    test_barcode = "3"

    def get_sample_row(self) -> RowT:
        row = SamplesImportTestCase.get_sample_row()
        row.update({SLIDE_BARCODE: self.test_barcode})
        return row

    def test_get_sample_ids(self):
        s1 = "s1"
        s4 = "s4"
        row = {
            SAMPLE1: s1,
            SAMPLE4: s4
        }
        self.assertEqual([s1, s4], SlidesImporter(row).get_sample_ids())

    def _test_sections(self, row: RowT, slide: Slide):
        sections = slide.section_set.all().order_by('number')
        for i, s in enumerate(sections):
            self.assertEqual(s.sample.name, row[SAMPLES[i]])

    def create_sample_slide(self) -> Slide:
        row = self.get_sample_row()
        si = SlidesImporter(row)
        si.import_slide()
        barcode = SlideBarcode.objects.get(name=self.test_barcode)
        slide = Slide.objects.get(barcode=barcode)
        self._test_sections(row, slide)
        return slide

    def test_import_slides(self):
        self.create_sample_slide()

    def test_import_different_slides_with_the_same_barcode(self):
        self.create_sample_slide()
        row = self.get_sample_row()
        new_row = {key: val for key, val in row.items() if not (key.endswith("_3") or key.endswith("_4"))}
        si = SlidesImporter(new_row)
        si.import_slide()
        barcode = SlideBarcode.objects.get(name=self.test_barcode)
        slides = Slide.objects.filter(barcode=barcode)
        for slide in slides:
            if len(slide.section_set.all()) == 4:
                self._test_sections(row, slide)
            else:
                self._test_sections(new_row, slide)
