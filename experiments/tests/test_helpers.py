import os
from typing import Dict

import pandas as pd
from django.test import TestCase

from experiments.xls.excel_row import ExcelRow
from experiments.constants import SLIDE_ID, AUTOMATED_SLIDEN, AUTOMATED_PLATEID


class ExcelRowTestCase(TestCase):
    file = "output.xlsx"

    def _write_in_file(self, row: Dict[str, str]):
        row = ExcelRow(row)
        row.write_in_file(self.file, 0)

    def test_overwriting_old_values(self):
        row1 = {SLIDE_ID: "val1"}
        self._write_in_file(row1)
        df = pd.read_excel(self.file)
        self.assertEqual(df.loc[0, SLIDE_ID], "val1")
        row2 = {AUTOMATED_PLATEID: "val2",
                AUTOMATED_SLIDEN: "val3"}
        self._write_in_file(row2)
        df = pd.read_excel(self.file)
        self.assertEqual(df.loc[0, AUTOMATED_PLATEID], "val2")
        self.assertEqual(df.loc[0, AUTOMATED_SLIDEN], "val3")
        self.assertTrue(pd.isnull(df.loc[0, SLIDE_ID]))

    def tearDown(self) -> None:
        os.remove(self.file)