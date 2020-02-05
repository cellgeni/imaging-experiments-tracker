import os
import uuid
from abc import abstractmethod
from typing import List

from django import forms
from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from experiments.xls import EXCEL_TEMPLATE, StreamLogging
from experiments.xls.import_xls import RowsImporter
from experiments.xls.column_importer import ColumnImporter


class XLSUploadForm(forms.Form):
    file = forms.FileField()


class XLSImportView(View):

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

    def post(self,  request, *args, **kwargs):
        form = XLSUploadForm(request.POST, request.FILES)
        if form.is_valid():
            data = self.handle_uploaded_file(request.FILES['file'])
        else:
            data = ["form invalid"]
        return render(request, 'xls.html', {'form': form,
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
        si = ColumnImporter(filename)
        with StreamLogging() as logger:
            si.import_all_columns()
            os.remove(filename)
            data = logger.get_log()
        log_list = data.split("\n")
        return log_list


class XLSTemplateDownloadView(View):

    def get(self, request, *args, **kwargs):
        with open(EXCEL_TEMPLATE, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=xls_template.xlsx'
        return response
