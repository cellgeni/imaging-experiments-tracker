import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaging_tracking.settings")
django.setup()

import xlsxwriter
from experiments.xls.write.template_columns import *
from experiments.xls import EXCEL_TEMPLATE


class MeasurementsSubmissionTemplateGenerator:
    def __init__(self, workbook, columns: List[ImageTrackerColumn]):
        self.workbook = workbook
        self.worksheet = workbook.add_worksheet()
        self.current_column = 0
        self.columns = columns

    def write_doc(self):
        for column in self.columns:
            column.write(self.current_column, self.worksheet)
            self.current_column += 1
        self.format_header()

    def format_header(self):
        header_format = self.workbook.add_format()
        header_format.set_bold(True)
        self.worksheet.set_row(0, 20, header_format)

    @classmethod
    def generate_template(cls, template_file=EXCEL_TEMPLATE):
        workbook = xlsxwriter.Workbook(template_file)
        w = cls(workbook, get_columns())
        w.write_doc()
        workbook.close()


if __name__ == "__main__":
    MeasurementsSubmissionTemplateGenerator.generate_template()
