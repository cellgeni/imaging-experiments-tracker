import io
import logging

from experiments.xls import xls_logger


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