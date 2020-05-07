import traceback
from typing import Iterable

import pandas as pd

from experiments.constants import REQUIRED_COLUMNS
from experiments.models import Measurement
from experiments.xls import xls_logger as logger, XLSImporter
from experiments.xls.measurement_importer import MeasurementImporter


class MeasurementsXLSImporter(XLSImporter):
    """Class that implements importing measurements from an Excel file"""

    def __init__(self, file):
        super().__init__(file)
        # TODO: add tests for this
        absent_required_columns = set(REQUIRED_COLUMNS).difference(set(self.df.columns))
        if absent_required_columns:
            logger.error(
                f"Required columns are absent from the spreadsheet or named incorrectly: {absent_required_columns}")
            raise ValueError()

    def get_rows(self) -> Iterable[pd.Series]:
        for _, row in self.df.iterrows():
            yield row

    def import_measurements(self) -> None:
        for i, row in enumerate(self.get_rows()):
            try:
                MeasurementImporter(row).import_measurement()
            except Exception as e:
                logger.error(f"Failed to import measurement with row number {i+1}")
                logger.error(e)
                traceback.print_exc()
