import logging
import os

import pandas as pd

EXCEL_TEMPLATE = os.path.join(os.path.dirname(__file__), "measurements_input.xlsx")

logging.basicConfig(level=logging.INFO)
xls_logger = logging.getLogger(__name__)


class ExcelImporter:

    def __init__(self, file):
        self.df = pd.read_excel(file).replace({pd.np.nan: None,
                                               'N/A': None})
