import traceback
import uuid
from typing import Iterable

import pandas as pd
from django.core.exceptions import ObjectDoesNotExist

from experiments.constants import *
from experiments.models import Measurement
from experiments.xls import xls_logger as logger
from experiments.xls.measurement_parameters import MeasurementParameters, MeasurementParametersParser


class MeasurementRow:
    """
    This is an intermediate entity that transforms ExcelRow into Measurement
    """

    def __init__(self, row: pd.Series):
        self._row = row
        self._uuid = self._row.get(UUID, uuid.uuid4())

    def get_uuid(self):
        return self._uuid

    def ignore(self) -> None:
        logger.info(f"Row ignored: {self.get_uuid()}")

    def delete(self) -> None:
        uuid = self.get_uuid()
        try:
            Measurement.objects.get(uuid=uuid).delete()
            logger.info(f"Deleted measurement with uuid {uuid}")
        except ObjectDoesNotExist:
            logger.warning(f"Measurement with uuid {uuid} does not exist")

    @staticmethod
    def create(parameters: MeasurementParameters) -> None:
        uuid = parameters.create_db_object()
        logger.info(f"Created measurement with uuid {uuid}")

    def update(self, parameters: MeasurementParameters) -> None:
        uuid = parameters.update_db_object()
        logger.info(f"Updated measurement with uuid {uuid}")

    def parse_parameters(self) -> MeasurementParameters:
        parser = MeasurementParametersParser(self._row)
        return parser.get_params()

    def create_or_update(self) -> None:
        parameters = self.parse_parameters()
        try:
            measurement = Measurement.objects.get(uuid=self.get_uuid())
            self.update(parameters)
        except ObjectDoesNotExist:
            self.create(parameters)

    def handle_mode(self) -> None:
        mode = self._row[MODE]
        if mode == IGNORE:
            self.ignore()
        elif mode == CREATE_OR_UPDATE:
            self.create_or_update()
        elif mode == DELETE:
            self.delete()


class ExcelImporter:

    def __init__(self, file):
        self.df = pd.read_excel(file)
        self.df.dropna()
        self.convert_floats_to_ints()

    def convert_floats_to_ints(self):
        cols = [AUTOMATED_SLIDEN]
        self.df[cols] = self.df[cols].astype('Int64')


class RowsImporter(ExcelImporter):

    def get_rows(self) -> Iterable[MeasurementRow]:
        for _, row in self.df.iterrows():
            yield MeasurementRow(row)

    def import_measurements(self) -> None:
        for row in self.get_rows():
            try:
                row.handle_mode()
            except Exception as e:
                logger.error(f"Failed to import measurement {row.get_uuid()}")
                logger.error(e)
                traceback.print_exc()

    def import_all(self):
        for _, row in self.df.iterrows():
            pass


if __name__ == "__main__":
    file = r'../measurements_input.xlsx'
    si = RowsImporter(file)
    si.import_measurements()
