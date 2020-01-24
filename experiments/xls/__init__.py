import io
import logging
import os

EXCEL_TEMPLATE = os.path.join(os.path.dirname(__file__), "measurements_input.xlsx")

logging.basicConfig(level=logging.INFO)
xls_logger = logging.getLogger(__name__)


class StreamLogging:

    def __init__(self):
        self._stream = io.StringIO()
        self.handler = logging.StreamHandler(self._stream)

    def __enter__(self) -> 'StreamLogging':
        xls_logger.addHandler(self.handler)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        xls_logger.removeHandler(self.handler)

    def get_log(self) -> str:
        return self._stream.getvalue()
