from experiments.constants import *
from experiments.models import Researcher, Project, Slide, Technology, LowMagReference, \
    MagBinOverlap, ZPlanes, TeamDirectory, ExportLocation, ArchiveLocation, Channel, Target
from experiments.populate.measurement import MeasurementsPrerequisitesPopulator
from experiments.tests.helpers import ExcelRowInfoGenerator, MeasurementImportBaseTestCase
from experiments.xls.measurement_importer import MeasurementImporter


class MeasurementImportTestCase(MeasurementImportBaseTestCase):

    def setUp(self):
        MeasurementsPrerequisitesPopulator.populate_all_prerequisites()

    def test_create_with_one_slot(self):
        row = ExcelRowInfoGenerator.get_sample_info()
        MeasurementImporter(row).import_measurement()
        self.check_row_is_in_database(row)

    def test_update_with_one_slot(self):
        row = ExcelRowInfoGenerator.get_sample_info()
        MeasurementImporter(row).import_measurement()
        self.check_row_is_in_database(row)
        ch1 = Channel.objects.get_or_create(name="channel1")
        ch2 = Channel.objects.get_or_create(name="channel2")
        t1 = Target.objects.get_or_create(name="t1")
        t2 = Target.objects.get_or_create(name="t2")
        t3 = Target.objects.get_or_create(name="t3")
        new_row_info = {
            RESEARCHER: str(Researcher.objects.last()),
            PROJECT: str(Project.objects.last()),
            SLIDE_BARCODE: str(Slide.objects.last().barcode),
            TECHNOLOGY: str(Technology.objects.last()),
            IMAGE_CYCLE: 4,
            TISSUE1: "some",
            SAMPLE1: "some",
            TISSUE2: "some2",
            SAMPLE2: "some2",
            TISSUE3: "some3",
            SAMPLE3: "some3",
            CHANNEL1: str(ch1),
            TARGET1: str(t1),
            CHANNEL2: str(ch2),
            TARGET2: str(t2),
            CHANNEL3: str(ch1),
            TARGET3: str(t2),
            CHANNEL4: str(ch2),
            TARGET4: str(t3),
            CHANNEL5: str(ch2),
            TARGET5: str(t3),
            LOW_MAG_REFERENCE: str(LowMagReference.objects.last()),
            MAG_BIN_OVERLAP: str(MagBinOverlap.objects.last()),
            SECTION_NUM: "2, 3",
            ZPLANES: str(ZPlanes.objects.last()),
            NOTES_1: "SMTH2",
            NOTES_2: "SMTH2",
            POST_STAIN: "smth2",
            HARMONY_COPY: "No",
            EXPORT_LOCATION: str(ExportLocation.objects.last()),
            ARCHIVE_LOCATION: str(ArchiveLocation.objects.last()),
            TEAM_DIR: str(TeamDirectory.objects.last()),
        }
        new_row = row.copy()
        new_row.update(new_row_info)
        self.check_row_is_in_database(new_row)
        with self.assertRaises(AssertionError):
            self.check_row_is_in_database(row)

    def test_find_existing_automated(self):
        pass

    def test_find_existing_manual(self):
        pass

    def test_append_new_slot_to_existing_automated_measurement(self):
        """
        Create an automated measurement.
        Create a row with the same measurement, different SlideID and samples
        Both rows must belong to the same measurement.
        """
        row = ExcelRowInfoGenerator.get_sample_info()
        m1 = MeasurementImporter(row).import_measurement()
        self.check_row_is_in_database(row)
        new_row_info = {
            SLIDE_BARCODE: str(Slide.objects.first().barcode),
            AUTOMATED_SLIDEN: 2,
            SLIDE_ID: "slide_2",
            TISSUE1: "slide_2",
            SAMPLE1: "slide_2",
            TISSUE2: "slide_2_1",
            SAMPLE2: "slide_2_1",
        }
        new_row = row.copy()
        new_row.update(new_row_info)
        m2 = MeasurementImporter(new_row).import_measurement()
        self.check_row_is_in_database(new_row)
        self.assertEqual(m1.id, m2.id)

    def test_incorrect_new_slot_for_existing_automated_measurement(self):
        """If slot contains a different measurement info, it should be dismissed"""
        pass

    def test_append_new_slot_to_existing_manual_measurement(self):
        row = ExcelRowInfoGenerator.get_sample_info()
        m1 = MeasurementImporter(row).import_measurement()
        self.check_row_is_in_database(row)
        new_row_info = {
            SLIDE_BARCODE: str(Slide.objects.last().barcode),
            AUTOMATED_SLIDEN: 2,
            TISSUE1: "slide_2",
            SAMPLE1: "slide_2",
            TISSUE2: "slide_2_1",
            SAMPLE2: "slide_2_1",
        }
        new_row = row.copy()
        new_row.update(new_row_info)
        m2 = MeasurementImporter(new_row).import_measurement()
        self.check_row_is_in_database(new_row)
        self.assertEqual(m1.id, m2.id)

    def test_update_slot_in_existing_manual_measurement(self):
        pass

    def test_update_slot_in_existing_automated_measurement(self):
        pass

    def test_required_missing(self):
        pass

    def test_invalid_keys(self):
        pass

    def test_insert_duplicate(self):
        pass

    def test_delete(self):
        pass
