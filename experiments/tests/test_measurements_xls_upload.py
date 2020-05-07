import logging

from django.test import TransactionTestCase

from experiments import RowT
from experiments.populate.measurement import MeasurementsPrerequisitesPopulator
from experiments.tests.helpers import ExcelRow, ExcelRowInfoGenerator, MeasurementImportBaseTestCase
from experiments.xls.file_importers import MeasurementsFileImporter, FileImporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MeasurementsUploadBase(TransactionTestCase):
    file = 'measurements_input2.xlsx'
    importer = FileImporter(file)

    def write_row_dict_in_file(self, row_dict: RowT) -> RowT:
        row = ExcelRow(row_dict)
        row.write_to_file(self.file)
        return row_dict

    def import_row_dict_into_db(self, row_dict: RowT) -> RowT:
        row = self.write_row_dict_in_file(row_dict)
        self.importer.import_file()
        return row

    def import_sample_row_into_db(self) -> RowT:
        return self.import_row_dict_into_db(ExcelRowInfoGenerator.get_sample_info())


class MeasurementsUploadTestCase(MeasurementsUploadBase, MeasurementImportBaseTestCase):
    file = 'measurements_input2.xlsx'
    importer = MeasurementsFileImporter(file)

    def setUp(self):
        p = MeasurementsPrerequisitesPopulator()
        p.populate_all_prerequisites()

    def test_object_creation(self):
        row = self.import_sample_row_into_db()
        self.check_row_is_in_database(row)
