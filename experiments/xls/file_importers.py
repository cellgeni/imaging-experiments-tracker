import enum
import os
from abc import abstractmethod
from typing import List, Type

from experiments.xls.stream_logging import StreamLogging
from experiments.xls.column_importer import ColumnExcelImporter
from experiments.xls.measurement_importer import MeasurementsExcelImporter


class FileImporterMode(enum.Enum):
    WHOLE_FILE = 1
    MEASUREMENTS = 2


class FileImporter:

    def __init__(self, filename: str):
        self.filename = filename

    def import_and_get_log(self) -> List[str]:
        with StreamLogging() as logger:
            try:
                self.import_file()
            except ValueError:
                pass
            finally:
                os.remove(self.filename)
                data = logger.get_log()
        log_list = data.split("\n")
        return log_list

    @abstractmethod
    def import_file(self) -> None:
        pass


class MeasurementsFileImporter(FileImporter):

    def import_file(self) -> None:
        si = MeasurementsExcelImporter(self.filename)
        si.import_measurements()


class EverythingFileImporter(FileImporter):

    def import_file(self) -> None:
        ci = ColumnExcelImporter(self.filename)
        ri = MeasurementsExcelImporter(self.filename)
        ci.import_all_columns()
        ri.import_measurements()


class FileImporterFactory:

    @classmethod
    def get_importer(cls, mode: FileImporterMode) -> Type[FileImporter]:
        if mode == FileImporterMode.WHOLE_FILE:
            return EverythingFileImporter
        elif mode == FileImporterMode.MEASUREMENTS:
            return MeasurementsFileImporter

