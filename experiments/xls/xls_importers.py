import traceback
from typing import Iterable, Dict

import pandas as pd

from experiments.constants import REQUIRED_COLUMNS, METABASE_CHANNEL_TARGETS, RESEARCHER, PROJECT, TECHNOLOGY, CHANNEL
from experiments.models import Researcher, Project, Technology, Channel
from experiments.xls import xls_logger as logger
from experiments.xls.measurement_importer import MeasurementImporter
from experiments.xls.xls_converters import MetabaseToTemplateConverter


class XLSImporter:
    """Base class for importing Excel files, contains Pandas dataframe with data."""

    def __init__(self, file: str):
        replacements = {pd.np.nan: None,
                        'N/A': None}
        self.df = pd.read_excel(file).replace(replacements)


class MeasurementsXLSImporter(XLSImporter):
    """Class that implements importing measurements from an Excel file"""

    def __init__(self, file: str, user_id: int):
        super().__init__(file)
        self.check_metabase_format()
        self.replace_old_researchers()
        self.check_required_columns()
        self.user_id = user_id

    def replace_old_researchers(self) -> None:
        """Function to replace old-style researcher abbreviations.
        To be deleted once all the existing spreadsheets are imported"""
        RESEARCHER_MAPPING = {
            'K_R': 'kr19',
            'KR': 'kr19',
            'ET': 'et2',
            'OB': 'ob5',
            'SP': 'sp25',
            'AA': 'aa16',
            'CJ': 'cj7',
            'CS': 'cs41',
            'EE': 'ee2',
            'JH': 'jh38',
            'JP': 'jp27',
            'JSP': 'jp27',
            'KK': 'kk15',
            'LR': 'lr17',
            'MD': 'md18',
            'TL': 'tl10'
        }
        self.df[RESEARCHER] = self.df[RESEARCHER].replace(RESEARCHER_MAPPING)

    def check_required_columns(self) -> None:
        """Check that the spreadsheet has all the required columns."""
        # TODO: tests
        absent_required_columns = set(REQUIRED_COLUMNS).difference(set(self.df.columns))
        if absent_required_columns:
            logger.error(f"Required columns are absent from the spreadsheet "
                         f"or named incorrectly: {absent_required_columns}")
            raise ValueError()

    def check_metabase_format(self) -> None:
        """Check if the spreadsheet is in metabase format. Convert to template format if so."""
        if METABASE_CHANNEL_TARGETS in self.df.columns:
            self.df = MetabaseToTemplateConverter(self.df).convert()

    def get_rows(self) -> Iterable[Dict]:
        for _, row in self.df.iterrows():
            yield row.to_dict()

    def import_measurements(self) -> None:
        for i, row in enumerate(self.get_rows()):
            try:
                MeasurementImporter(row, self.user_id).import_measurement()
            except Exception as e:
                logger.error(f"Failed to import measurement with row number {i + 1}")
                logger.error(e)
                traceback.print_exc()

    def delete_measurements(self):
        for i, row in enumerate(self.get_rows()):
            try:
                if MeasurementImporter(row, self.user_id).delete_measurement():
                    logger.info(f"Deleted measurement with row number {i + 1}")
                else:
                    logger.info(f"Measurement with row number {i + 1} does not exist in the database")
            except Exception as e:
                logger.error(f"Failed to delete measurement with row number {i + 1}")
                logger.error(e)
                traceback.print_exc()


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
