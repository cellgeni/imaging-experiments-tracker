import logging

import pandas as pd
from django.test import TransactionTestCase

from experiments import RowT
from experiments.constants import *
from experiments.models import Channel, Researcher, Project, Technology
from experiments.populate.measurement import MeasurementsPrerequisitesPopulator
from experiments.tests.helpers import ExcelRow, ExcelRowInfoGenerator, MeasurementImportBaseTestCase
from experiments.xls.view_importers import MeasurementsViewImporter, ViewImporter
from experiments.xls.xls_converters import MetabaseToTemplateConverter, MetabaseColumnGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MeasurementsUploadBase(MeasurementImportBaseTestCase, TransactionTestCase):
    file = 'measurements_input2.xlsx'
    importer = ViewImporter(file)

    def write_row_dict_in_file(self, row_dict: RowT) -> RowT:
        row = ExcelRow(row_dict)
        row.write_to_file(self.file)
        return row_dict

    def import_row_dict_into_db(self, row_dict: RowT) -> RowT:
        row = self.write_row_dict_in_file(row_dict)
        self.importer.import_file()
        return row

    def import_sample_row_into_db(self) -> RowT:
        row = self.import_row_dict_into_db(ExcelRowInfoGenerator.get_sample_info())
        self.check_row_is_in_database(row)
        return row


class TemplateUploadTestCase(MeasurementsUploadBase):
    file = 'measurements_input2.xlsx'
    importer = MeasurementsViewImporter(file)

    def setUp(self):
        p = MeasurementsPrerequisitesPopulator()
        p.populate_all_prerequisites()

    def test_object_creation(self):
        self.import_sample_row_into_db()


class MetabaseRowImportTestCase(MeasurementsUploadBase, MeasurementImportBaseTestCase):
    importer = MeasurementsViewImporter(MeasurementsUploadBase.file)

    def setUp(self):
        MeasurementsPrerequisitesPopulator.populate_all_prerequisites()

    def check_metabase_row_is_in_database(self, row):
        template_row = MetabaseToTemplateConverter(pd.DataFrame(row)).convert()
        self.check_row_is_in_database(template_row[0].to_dict())

    def test_update(self):
        """
        Create a measurement, then create the same measurement with different updatable attributes in Metabase format.
        Check that the original measurement is gone, the new one is in the database.
        """
        row = self.import_sample_row_into_db()
        ch1 = Channel.objects.get_or_create(name="channel1")[0]
        ch2 = Channel.objects.get_or_create(name="channel2")[0]
        t1 = "t1"
        t2 = "t2"
        t3 = "t3"
        template_channel_targets = {
            CHANNEL1: str(ch1),
            TARGET1: str(t1),
            CHANNEL2: str(ch2),
            TARGET2: str(t2),
            CHANNEL3: str(ch1),
            TARGET3: str(t2),
            CHANNEL4: str(ch2),
            TARGET4: str(t3),
            CHANNEL5: str(ch2),
            TARGET5: str(t3)
        }
        metabase_channel_targets = MetabaseColumnGenerator.generate_channel_targets(template_channel_targets)
        template_samples = {
            SAMPLE1: "A29-HEA-2-FFPE-1-S14-iii",
            TISSUE1: "Heart (R ventricle)",
            AGE1: "age_1",
            GENOTYPE1: "genotype_1",
            BACKGROUND1: "background_1",
            SAMPLE2: "A29-HEA-3-FFPE-1-S10-ii",
            TISSUE2: "tissue_2",
            AGE2: "age2",
            GENOTYPE2: "gen2",
            BACKGROUND2: "back2",
            SAMPLE3: "A29-HEA-4-FFPE-1-S6-i",
            TISSUE3: "tissue4",
            SECTION_NUM: "1, 2, 3"
        }
        metabase_samples = MetabaseColumnGenerator.generate_samples(template_samples)
        new_row_metabase = {
            METABASE_RESEARCHER: str(Researcher.objects.last()),
            METABASE_PROJECT: str(Project.objects.last()),
            METABASE_TECHNOLOGY: str(Technology.objects.last()),
            METABASE_MEASUREMENT_NUMBER: row[MEASUREMENT_NUMBER],
            METABASE_DATE: MetabaseColumnGenerator.generate_date(row[DATE]),
            METABASE_AUTOMATED_PLATEID: row.get(AUTOMATED_PLATEID),
            METABASE_AUTOMATED_SLIDEN: row[AUTOMATED_SLIDEN],
            METABASE_SLIDE_ID: row[SLIDE_ID],
            METABASE_SLIDE_BARCODE: "4",
            METABASE_IMAGE_CYCLE: 4,
            METABASE_SAMPLES: metabase_samples,
            METABASE_CHANNEL_TARGETS: metabase_channel_targets,
            METABASE_LOW_MAG_REFERENCE: "some",
            METABASE_MAG_BIN_OVERLAP: "some",
            METABASE_ZPLANES: "some",
            METABASE_NOTES_1: "SMTH2",
            METABASE_NOTES_2: "SMTH2",
            METABASE_POST_STAIN: "smth2",
            METABASE_HARMONY_COPY: False,
            METABASE_EXPORT_LOCATION: "some",
            METABASE_ARCHIVE_LOCATION: "some",
            METABASE_TEAM_DIR: "some",
        }
        new_row_template = {
            RESEARCHER: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[RESEARCHER]],
            PROJECT: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[PROJECT]],
            TECHNOLOGY: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[TECHNOLOGY]],
            MEASUREMENT_NUMBER: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[MEASUREMENT_NUMBER]],
            DATE: row[DATE],
            AUTOMATED_PLATEID: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[AUTOMATED_PLATEID]],
            AUTOMATED_SLIDEN: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[AUTOMATED_SLIDEN]],
            SLIDE_ID: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[SLIDE_ID]],
            SLIDE_BARCODE: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[SLIDE_BARCODE]],
            IMAGE_CYCLE: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[IMAGE_CYCLE]],
            LOW_MAG_REFERENCE: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[LOW_MAG_REFERENCE]],
            MAG_BIN_OVERLAP: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[MAG_BIN_OVERLAP]],
            ZPLANES: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[ZPLANES]],
            NOTES_1: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[NOTES_1]],
            NOTES_2: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[NOTES_2]],
            POST_STAIN: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[POST_STAIN]],
            HARMONY_COPY: "No",
            EXPORT_LOCATION: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[EXPORT_LOCATION]],
            ARCHIVE_LOCATION: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[ARCHIVE_LOCATION]],
            TEAM_DIR: new_row_metabase[TEMPLATE_TO_METABASE_MAPPING[TEAM_DIR]],
        }
        new_row_template.update(template_samples)
        new_row_template.update(template_channel_targets)
        file = "metabase.xlsx"
        pd.DataFrame([new_row_metabase]).to_excel(file)
        MeasurementsViewImporter(file).import_file()
        self.check_row_is_in_database(new_row_template)
        with self.assertRaises(AssertionError):
            self.check_row_is_in_database(row)
