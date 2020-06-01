from django.test import TestCase

from experiments.xls import xls_logger
from experiments.xls.stream_logging import StreamLogging


class StreamLoggingTestCase(TestCase):

    def test_logging(self):
        s1 = "a test string"
        s2 = "another test string"
        result = f"INFO::{s1}\nERROR::{s2}\n"
        with StreamLogging() as stream:
            xls_logger.info(s1)
            xls_logger.error(s2)
            data = stream.get_log()
        self.assertEqual(result, data)

    def test_handlers(self):
        self.assertFalse(xls_logger.handlers)
        with StreamLogging() as s:
            self.assertTrue(xls_logger.handlers)
        self.assertFalse(xls_logger.handlers)