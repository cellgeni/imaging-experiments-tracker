import os
import uuid
from typing import List

from django import forms
from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from experiments.xls import EXCEL_TEMPLATE
from xls import StreamLogging
from xls.import_xls import SpreadsheetImporter


class XLSUploadForm(forms.Form):
    file = forms.FileField()


class MeasurementXLSImportView(View):

    def get(self, request, *args, **kwargs):
        form = XLSUploadForm()
        return render(request, 'xls.html', {'form': form})

    def _write_file(self, f, filename):
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def handle_uploaded_file(self, f: File) -> List[str]:
        filename = str(uuid.uuid4()) + ".xlsx"
        self._write_file(f, filename)
        si = SpreadsheetImporter(filename)
        with StreamLogging() as logger:
            si.import_spreadsheet()
            os.remove(filename)
            data = logger.get_log()
        log_list = data.split("\n")
        return log_list

    def post(self,  request, *args, **kwargs):
        form = XLSUploadForm(request.POST, request.FILES)
        if form.is_valid():
            data = self.handle_uploaded_file(request.FILES['file'])
        else:
            data = ["form invalid"]
        return render(request, 'xls.html', {'form': form,
                                            'data': data})


class XLSTemplateDownloadView(View):

    def get(self, request, *args, **kwargs):
        with open(EXCEL_TEMPLATE, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=xls_template.xlsx'
        return response
