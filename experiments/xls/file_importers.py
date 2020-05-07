import enum
import os
from abc import abstractmethod
from typing import List, Type

from experiments.xls.stream_logging import StreamLogging
from experiments.xls.keys_importer import ColumnXLSImporter
from experiments.xls.measurement_xls_importer import MeasurementsXLSImporter


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
        si = MeasurementsXLSImporter(self.filename)
        si.import_measurements()


class KeysFileImporter(FileImporter):

    def import_file(self) -> None:
        ci = ColumnXLSImporter(self.filename)
        ri = MeasurementsXLSImporter(self.filename)
        ci.import_all_columns()
        ri.import_measurements()


class FileImporterFactory:

    @classmethod
    def get_importer(cls, mode: FileImporterMode) -> Type[FileImporter]:
        if mode == FileImporterMode.WHOLE_FILE:
            return KeysFileImporter
        elif mode == FileImporterMode.MEASUREMENTS:
            return MeasurementsFileImporter

