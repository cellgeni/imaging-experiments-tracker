import datetime
from abc import abstractmethod
from typing import List

import jwt
from django.conf import settings
from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from experiments.forms import XLSUploadForm
from experiments.xls import EXCEL_TEMPLATE
from experiments.xls.file_importers import FileImporterMode, FileImporterFactory
from experiments.xls.write.generate_template import MeasurementsSubmissionTemplateGenerator
from experiments.xls.write.writer import ExcelFileWriter


class XLSProcessView(View):
    """
    Generic view to serve as a base for other views that import an Excel file
    """

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
            log = self.dump_file_on_disk_import_it_and_get_import_log(
                request.FILES['file'])
        else:
            log = ["Invalid submission"]
        return render(request, self.template_name, {'form': form,
                                                    'log': log})


class MeasurementXLSImportView(XLSProcessView):
    """
    Imports measurements from an XLS file
    """

    def get_mode(self) -> FileImporterMode:
        return FileImporterMode.MEASUREMENTS


class WholeFileXLSImportView(XLSProcessView):
    """
    Imports all columns from an XLS file
    """

    def get_mode(self) -> FileImporterMode:
        return FileImporterMode.WHOLE_FILE


class XLSDeleteView(XLSProcessView):
    """Delete measurements from a file"""

    def get_mode(self) -> FileImporterMode:
        return FileImporterMode.DELETE


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
        MeasurementsSubmissionTemplateGenerator.generate_template(file)
        return self.serve_excel(file, request)


class DataView(View):
    """
    View to serve embedded metabase question
    """

    def get(self, request, *args, **kwargs):
        payload = {
            "resource": {"question": 1},
            "params": {"authorized_projects": None},
            # 10 minute expiration in miliseconds
            "exp": int((datetime.datetime.now() +
                        datetime.timedelta(minutes=10)
                        ).timestamp()) * 1000
        }

        token = jwt.encode(
            payload, settings.METABASE_SECRET_KEY, algorithm="HS256")

        iframe_url = "{url}/embed/question/{token}".format(
            url=settings.METABASE_SITE_URL, token=token.decode('UTF-8'))

        return render(request, 'dataview.html', {'iframeUrl': iframe_url})
