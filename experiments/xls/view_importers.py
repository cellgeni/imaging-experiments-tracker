from abc import abstractmethod
from experiments.models import user
from typing import List

from experiments.xls.stream_logging import StreamLogging
from experiments.xls.xls_importers import MeasurementsXLSImporter, ColumnXLSImporter


class ViewImporter:
    """A class to represent a handler for different views"""

    def __init__(self, filename: str, user_id: int):
        self.filename = filename
        self.user_id = user_id

    def import_and_get_log(self) -> List[str]:
        with StreamLogging() as logger:
            try:
                self.import_file()
            except ValueError as e:
                return [f"Could not import the file f{self.filename}, error message: {e}"]
            finally:
                data = logger.get_log()
        log_list = data.split("\n")
        return log_list

    @abstractmethod
    def import_file(self) -> None:
        pass


class MeasurementsViewImporter(ViewImporter):

    def import_file(self) -> None:
        si = MeasurementsXLSImporter(self.filename, self.user_id)
        si.import_measurements()


class KeysViewImporter(ViewImporter):

    def import_file(self) -> None:
        ci = ColumnXLSImporter(self.filename)
        ci.import_all_columns()


class DeletionViewImporter(ViewImporter):

    def import_file(self) -> None:
        si = MeasurementsXLSImporter(self.filename, self.user_id)
        si.delete_measurements()
