import uuid
from abc import abstractmethod
from typing import List

from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from experiments.forms import XLSUploadForm, UUIDGeneratorForm
from experiments.xls import EXCEL_TEMPLATE
from experiments.xls.file_importers import FileImporterMode, FileImporterFactory
from experiments.xls.write.generate_template import ImageTrackerWriter
from experiments.xls.write.writer import ExcelFileWriter
from xls.write.inject_uuids_and_modes import ColumnInjector


class XLSImportView(View):
    template_name = "xls.html"

    def get(self, request, *args, **kwargs):
        form = XLSUploadForm()
        return render(request, 'xls.html', {'form': form})

    def dump_file_on_disk_import_it_and_get_import_log(self, f: File) -> List[str]:
        filename = ExcelFileWriter.dump_file_on_disk(f)
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
            log = ["Invalid submission"]
        return render(request, self.template_name, {'form': form,
                                                    'log': log})


class MeasurementXLSImportView(XLSImportView):

    def get_mode(self) -> FileImporterMode:
        return FileImporterMode.MEASUREMENTS


class ColumnsXLSImportView(XLSImportView):

    def get_mode(self) -> FileImporterMode:
        return FileImporterMode.EVERYTHING


class ExcelDownloadView(View):
    """
    Generic view to serve as a base for other views that return an Excel file
    """

    def serve_excel(self, file: str, request) -> HttpResponse:
        with open(file, "rb") as excel:
            data = excel.read()
        response = HttpResponse(data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename={file}'
        return response


class XLSTemplateDownloadView(ExcelDownloadView):
    """
    Generates an Excel template with prevalidated fields to upload new measurements
    """

    def get(self, request, *args, **kwargs):
        file = EXCEL_TEMPLATE
        ImageTrackerWriter.generate_template(file)
        return self.serve_excel(file, request)


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


class UUIDAndCreateModeInjectorView(XLSImportView, ExcelDownloadView):
    """
    Accepts an Excel file and returns the same file with UUID and Mode columns populated
    Mode column has value "Create or update" for all measurements
    """

    def inject_columns(self, request) -> HttpResponse:
        filename = request.FILES['file'].name.replace(" ", "_")
        ExcelFileWriter.dump_file_on_disk(request.FILES['file'], filename)
        ColumnInjector(filename).inject_uuid_mode_columns()
        return self.serve_excel(filename, request)

    def post(self, request, *args, **kwargs):
        form = XLSUploadForm(request.POST, request.FILES)
        if form.is_valid():
            return self.inject_columns(request)
        else:
            log = ["form invalid"]
        return render(request, self.template_name, {'form': form,
                                                    'log': log})
