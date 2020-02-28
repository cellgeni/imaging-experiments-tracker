import os
import uuid
from abc import abstractmethod
from typing import List

from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from experiments.forms import XLSUploadForm, UUIDGeneratorForm
from experiments.xls import EXCEL_TEMPLATE, StreamLogging
from experiments.xls.column_importer import ColumnImporter
from experiments.xls.generate.generate_template import ImageTrackerWriter
from experiments.xls.import_xls import RowsImporter


class XLSImportView(View):
    template_name = "xls.html"

    def get(self, request, *args, **kwargs):
        form = XLSUploadForm()
        return render(request, 'xls.html', {'form': form})

    def _write_file(self, f, filename):
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    @abstractmethod
    def handle_data(self, filename):
        pass

    def handle_uploaded_file(self, f: File) -> List[str]:
        filename = str(uuid.uuid4()) + ".xlsx"
        self._write_file(f, filename)
        return self.handle_data(filename)

    def post(self, request, *args, **kwargs):
        form = XLSUploadForm(request.POST, request.FILES)
        if form.is_valid():
            data = self.handle_uploaded_file(request.FILES['file'])
        else:
            data = ["form invalid"]
        return render(request, self.template_name, {'form': form,
                                                    'data': data})


class MeasurementXLSImportView(XLSImportView):

    def handle_data(self, filename):
        si = RowsImporter(filename)
        with StreamLogging() as logger:
            si.import_measurements()
            os.remove(filename)
            data = logger.get_log()
        log_list = data.split("\n")
        return log_list


class ColumnsXLSImportView(XLSImportView):

    def handle_data(self, filename):
        ci = ColumnImporter(filename)
        ri = RowsImporter(filename)
        with StreamLogging() as logger:
            ci.import_all_columns()
            ri.import_measurements()
            os.remove(filename)
            data = logger.get_log()
        log_list = data.split("\n")
        return log_list


class XLSTemplateDownloadView(View):

    def get(self, request, *args, **kwargs):
        file = EXCEL_TEMPLATE
        ImageTrackerWriter.generate_template(file)
        with open(file, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=xls_template.xlsx'
        return response


class UUIDGeneratorView(View):
    """
    Generates a given number of UUIDs that users can then copy-paste in their Excel spreadsheets to uniquely
    identify measurements
    """
    template_name = "uuids.html"

    def get(self, request, *args, **kwargs):
        form = UUIDGeneratorForm(request.GET)
        if form.is_valid():
            uuids = [uuid.uuid4() for x in range(int(request.GET['quantity']))]
        else:
            uuids = []
            form = UUIDGeneratorForm()
        return render(request, self.template_name, {'form': form,
                                                    'uuids': uuids})
