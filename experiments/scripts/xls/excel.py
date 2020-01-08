import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaging_tracking.settings")
django.setup()

import xlsxwriter
from xls.columns_export import *

workbook = xlsxwriter.Workbook('measurements_input.xlsx')
worksheet = workbook.add_worksheet()


class ImageTrackerWriter:
    def __init__(self, worksheet, columns: List[ImageTrackerColumn]):
        self.worksheet = worksheet
        self.current_column = 0
        self.columns = columns

    def write_mode(self):
        column = self.current_column
        for row in range(1, 21):
            self.worksheet.write(row, column, "Ignore")
        self.worksheet.data_validation(1, column, MAX_ROWS, column,
                                       {'validate': 'list',
                                        'value': MODES,
                                        'input_title': "Mode",
                                        'input_message': "Choose mode"})

    def write_researcher(self):
        column = self.current_column
        self.worksheet.write(0, column, RESEARCHER)
        self.worksheet.data_validation(1, column, MAX_ROWS, column,
                                       )

    def write_project(self):
        column = self.current_column
        self.worksheet.write(0, column, PROJECT)
        self.worksheet.data_validation(1, column, MAX_ROWS, column,
                                       {'validate': 'list',
                                        'value': [pr.key for pr in CellGenProject.objects.all()],
                                        'input_title': "Project",
                                        'input_message': "Choose researcher"})

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
