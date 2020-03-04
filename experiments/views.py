import uuid
from abc import abstractmethod
from typing import List

from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from experiments.forms import XLSUploadForm, UUIDGeneratorForm
from experiments.xls import EXCEL_TEMPLATE
from experiments.xls.generate.generate_template import ImageTrackerWriter
from xls.file_importers import FileImporterMode, FileImporterFactory


class XLSImportView(View):
    template_name = "xls.html"

    def get(self, request, *args, **kwargs):
        form = XLSUploadForm()
        return render(request, 'xls.html', {'form': form})

    def _write_file(self, f, filename):
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def dump_file_on_disk_import_it_and_get_import_log(self, f: File) -> List[str]:
        filename = str(uuid.uuid4()) + ".xlsx"
        self._write_file(f, filename)
        mode = self.get_mode()
        return FileImporterFactory.get_importer(mode)(filename).import_and_get_log()

    @abstractmethod
    def get_mode(self) -> FileImporterMode:
        pass

    def post(self, request, *args, **kwargs):
        form = XLSUploadForm(request.POST, request.FILES)
        if form.is_valid():
            log = self.dump_file_on_disk_import_it_and_get_import_log(request.FILES['file'])
        else:
            log = ["form invalid"]
        return render(request, self.template_name, {'form': form,
                                                    'log': log})


class MeasurementXLSImportView(XLSImportView):

    def get_mode(self) -> FileImporterMode:
        return FileImporterMode.MEASUREMENTS


class ColumnsXLSImportView(XLSImportView):

    def get_mode(self) -> FileImporterMode:
        return FileImporterMode.EVERYTHING


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
