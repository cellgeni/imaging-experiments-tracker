import logging
import os

import pandas as pd

from experiments.constants import AUTOMATED_SLIDEN

EXCEL_TEMPLATE = os.path.join(os.path.dirname(__file__), "measurements_input.xlsx")

logging.basicConfig(level=logging.INFO)
xls_logger = logging.getLogger(__name__)


class ExcelImporter:

    def __init__(self, file):
        self.df = pd.read_excel(file)
        self.df = self.df.replace({pd.np.nan: None})
