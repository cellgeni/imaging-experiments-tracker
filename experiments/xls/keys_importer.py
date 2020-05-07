import traceback
from functools import wraps

from experiments.models import *
from experiments.xls import xls_logger as logger, XLSImporter


def log_errors(func):
    """
    A decorator that captures an Exception and prints traceback
    """

    @wraps(func)
    def f(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            logger.error(e)
        # func(*args, **kwargs)

    return f


class ColumnXLSImporter(XLSImporter):
    """
    Imports particular columns from an Excel file
    """

    def import_researchers(self) -> None:
        self.df[RESEARCHER].apply(lambda key: Researcher.objects.get_or_create(login=key) if key else None)

    def import_projects(self) -> None:
        self.df[PROJECT].apply(lambda name: Project.objects.get_or_create(name=name) if name else None)

    def import_technology(self) -> None:
        self.df[TECHNOLOGY].apply(lambda name: Technology.objects.get_or_create(name=name) if name else None)

    def import_channels(self) -> None:
        self.df[CHANNEL].apply(lambda name: Channel.objects.get_or_create(name=name) if name else None)

    def import_all_columns(self):
        self.df.dropna()
        self.import_researchers()
        self.import_projects()
        self.import_technology()
        self.import_channels()
