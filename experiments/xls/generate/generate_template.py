import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaging_tracking.settings")
django.setup()

import xlsxwriter
from experiments.xls.generate.template_columns import *
from experiments.xls import EXCEL_TEMPLATE

workbook = xlsxwriter.Workbook(EXCEL_TEMPLATE)
worksheet = workbook.add_worksheet()


class ImageTrackerWriter:
    def __init__(self, worksheet, columns: List[ImageTrackerColumn]):
        self.worksheet = worksheet
        self.current_column = 0
        self.columns = columns

    def write_doc(self):
        for column in self.columns:
            column.write(self.current_column, self.worksheet)
            self.current_column += 1
        self.format_header()

    def format_header(self):
        header_format = workbook.add_format()
        header_format.set_bold(True)
        self.worksheet.set_row(0, 20, header_format)


w = ImageTrackerWriter(worksheet, get_columns())
w.write_doc()

workbook.close()
