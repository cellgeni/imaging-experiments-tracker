import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaging_tracking.settings")
django.setup()

import xlsxwriter
from experiments.xls import EXCEL_TEMPLATE
from experiments.constants import EXCEL_COLUMNS


class MeasurementsSubmissionTemplateGenerator:
    def __init__(self, workbook):
        self.workbook = workbook
        self.worksheet = workbook.add_worksheet()
        self.current_column = 0

    def write_doc(self):
        for column_header in EXCEL_COLUMNS:
            self.worksheet.write(0, self.current_column, column_header)
            self.current_column += 1
        self.format_header()

    def format_header(self):
        header_format = self.workbook.add_format()
        header_format.set_bold(True)
        self.worksheet.set_row(0, 20, header_format)

    @classmethod
    def generate_template(cls, template_file=EXCEL_TEMPLATE):
        """Generate a template file mimicking Measurements template for testing purposes."""
        workbook = xlsxwriter.Workbook(template_file)
        w = cls(workbook)
        w.write_doc()
        workbook.close()


if __name__ == "__main__":
    MeasurementsSubmissionTemplateGenerator.generate_template()
