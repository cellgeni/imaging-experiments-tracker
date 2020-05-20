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
    A parser that converts raw logs into dicts for ease of use
    """

    def __init__(self, raw_logs=[]):
        self.raw_logs = raw_logs
        self.logs = []
        self.parse_logs(self.raw_logs)

    def parse_logs(self, raw_logs):
        for log in raw_logs:
            self.parse(log)

    def parse(self, raw_log):
        if not raw_log:
            return
        log_tuple = raw_log.split('::')
        if len(log_tuple) == 2:
            self.add(log_tuple[0], log_tuple[1])
        else:
            self.add_error(raw_log)

    def add(self, level, message):
        self.logs.append({"level": level, "message": message})

    def add_error(self, message):
        self.logs.append({"level": "ERROR", "message": message})

    def get_logs(self):
        return self.logs

    def get_raw_logs(self):
        return self.raw_logs

    def get_error_count(self):
        return len([l for l in self.logs if l['level'] != "INFO"])
