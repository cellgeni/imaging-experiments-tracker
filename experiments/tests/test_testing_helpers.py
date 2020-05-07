import os
from typing import Dict

import pandas as pd
from django.test import TestCase

from experiments.constants import RESEARCHER, SLIDE_ID, AUTOMATED_PLATEID, AUTOMATED_SLIDEN
from experiments.populate.measurement import MeasurementsPrerequisitesPopulator
from experiments.tests.helpers import ExcelRow, ExcelRowInfoGenerator
from experiments.tests.test_measurements_xls_upload import logger


class ExcelRowTestCase(TestCase):
    file = 'measurements_input1.xlsx'

    def setUp(self) -> None:
        MeasurementsPrerequisitesPopulator.populate_all_prerequisites()

    def test_write_row(self) -> None:
        """Test whether ExcelRow correctly writes information in an Excel spreadsheet."""
        sample_info = ExcelRowInfoGenerator.get_sample_info()
        self.assertTrue(sample_info[RESEARCHER])
        row = ExcelRow(sample_info)
        row.write_to_file(self.file)
        df = pd.read_excel(self.file)
        for key, value in sample_info.items():
            spreadsheet_value = df.loc[0, key]
            logger.debug(f"Key: {key}")
            logger.debug(f"Original value: {value}")
            logger.debug(f"Spreadsheet value: {spreadsheet_value}")
            self.assertEqual(value, spreadsheet_value)

    def _write_in_file(self, row: Dict[str, str]):
        row = ExcelRow(row)
        row.write_to_file(self.file, 0)

    def test_overwriting_old_values(self):
        """Test whether ExcelRow correctly overwrites old information in an Excel spreadsheet."""
        row1 = {SLIDE_ID: "val1"}
        self._write_in_file(row1)
        df = pd.read_excel(self.file)
        self.assertEqual(df.loc[0, SLIDE_ID], row1[SLIDE_ID])
        row2 = {AUTOMATED_PLATEID: "val2",
                AUTOMATED_SLIDEN: "val3"}
        self._write_in_file(row2)
        df = pd.read_excel(self.file)
        self.assertEqual(df.loc[0, AUTOMATED_PLATEID], row2[AUTOMATED_PLATEID])
        self.assertEqual(df.loc[0, AUTOMATED_SLIDEN], row2[AUTOMATED_SLIDEN])
        self.assertTrue(pd.isnull(df.loc[0, SLIDE_ID]))

    def tearDown(self) -> None:
        os.remove(self.file)
