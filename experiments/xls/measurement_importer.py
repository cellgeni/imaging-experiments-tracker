import traceback
import uuid
from typing import Iterable

import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from experiments.constants import *
from experiments.models import Measurement
from experiments.xls import xls_logger as logger, ExcelImporter
from experiments.xls.measurement_parameters import MeasurementParameters, MeasurementParametersParser

REQUIRED_COLUMNS = {UUID, MODE, RESEARCHER, PROJECT, SLIDE_ID, SLIDE_BARCODE,
                    IMAGE_CYCLE, DATE, MAG_BIN_OVERLAP, SECTION_NUM}


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
        try:
            uuid = parameters.create_db_object()
        except IntegrityError as e:
            logger.error(f"Failed to create measurement with uuid {parameters.model.uuid}")
            logger.error(e)
        else:
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
        except Measurement.DoesNotExist:
            self.create(parameters)

    def handle_mode(self) -> None:
        mode = MeasurementModes(self._row[MODE])
        if mode == MeasurementModes.IGNORE:
            self.ignore()
        elif mode == MeasurementModes.CREATE_OR_UPDATE:
            self.create_or_update()
        elif mode == MeasurementModes.DELETE:
            self.delete()


class MeasurementsExcelImporter(ExcelImporter):

    def __init__(self, file):
        super().__init__(file)
        absent_required_columns = REQUIRED_COLUMNS.difference(set(self.df.columns))
        if absent_required_columns:
            logger.error(
                f"Required columns are absent from the spreadsheet or named incorrectly: {absent_required_columns}")
            raise ValueError()

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
