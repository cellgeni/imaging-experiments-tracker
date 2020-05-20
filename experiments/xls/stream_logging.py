import io
import logging

from experiments.xls import xls_logger


class StreamLogging:
    """
    A context manager that captures log messages and retains them in one string
    """

    def __init__(self):
        self._stream = io.StringIO()
        self.handler = logging.StreamHandler(self._stream)
        self.handler.setFormatter(
            logging.Formatter("%(levelname)s::%(message)s"))

    def __enter__(self) -> 'StreamLogging':
        xls_logger.addHandler(self.handler)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        xls_logger.removeHandler(self.handler)

    def get_log(self) -> str:
        return self._stream.getvalue()


class LogParser(object):
    """
    Current logging records are generated as strings with the following
    format "LEVEL::MESSAGE". This parser takes the raw log strings and turns
    them into a dictionary for ease of access of the level and message props.
    """

    def __init__(self, raw_logs: [str] = []):
        self.raw_logs = raw_logs
        self.logs = []
        self.parse_logs(self.raw_logs)

    def parse_logs(self, raw_logs: [str]):
        for log in raw_logs:
            self.parse_log_line(log)

    def parse_log_line(self, raw_log: str):
        """
        Example:
            - input [raw_log] = "INFO::Imported with id 99"
            - output [dict] = {"level": "INFO", "message": "Imported with id 99"}
        """
        if not raw_log:
            return
        log_tuple = raw_log.split('::')
        if len(log_tuple) == 2:
            self.add_message(log_tuple[0], log_tuple[1])
        else:
            self.add_error_message(raw_log)

    def add_message(self, level: str, message: str) -> dict():
        self.logs.append({"level": level, "message": message})

    def add_error_message(self, message: str) -> dict():
        self.add("ERROR", message)

    def get_error_count(self) -> int:
        return len([l for l in self.logs if l['level'] == "ERROR"])
