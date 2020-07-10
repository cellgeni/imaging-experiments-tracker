import os
from typing import Iterable

from django.test import TestCase

from experiments import RowT
from experiments.constants import RESEARCHER, PROJECT, TECHNOLOGY, CHANNEL
from experiments.models import *
from experiments.tests.helpers import ExcelRowWriter
from experiments.xls.xls_importers import ColumnXLSImporter


class SpreadsheetImportTestCase(TestCase):
    file = 'columns_input1.xlsx'

    def get_data(self) -> Iterable[RowT]:
        return [{
            RESEARCHER: "AR",
            PROJECT: "TM_R2C",
            TECHNOLOGY: "some technology",
            CHANNEL: "DAPI",
        }, {
            RESEARCHER: "MR",
            PROJECT: "TM_S2C",
            TECHNOLOGY: "some technology2",
            CHANNEL: "DAPI",
        }]

    def import_data(self) -> None:
        si2 = ColumnXLSImporter(self.file)
        si2.import_all_columns()

    def create_rows(self, rows: Iterable[RowT]):
        for i, r in enumerate(rows):
            row = ExcelRowWriter(r)
            row.write_in_file(self.file, i)
        self.import_data()

    def _test_row(self, row: RowT):
        self.assertTrue(Researcher.objects.get(login=row.get(RESEARCHER)))
        self.assertTrue(Project.objects.get(name=row.get(PROJECT)))
        self.assertTrue(Technology.objects.get(name=row.get(TECHNOLOGY)))
        self.assertTrue(Channel.objects.get(name=row.get(CHANNEL)))

    def test_spreadsheet_upload(self):
        """Test uploading a spreadsheet with keys and creating appropriate instances of models."""
        rows = self.get_data()
        self.create_rows(rows)
        for row in rows:
            self._test_row(row)

    def tearDown(self) -> None:
        os.remove(self.file)
