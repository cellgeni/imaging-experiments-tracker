# urls.py
from django.urls import path
from django.views.generic import RedirectView

from experiments.views import MeasurementXLSImportView, XLSTemplateDownloadView, ColumnsXLSImportView, UUIDGeneratorView

urlpatterns = [
    path('', RedirectView.as_view(url='/import/'), name='go-to-import'),
    path('import/', MeasurementXLSImportView.as_view(), name='upload-xls'),
    path('columns/', ColumnsXLSImportView.as_view()),
    path('xls-template/', XLSTemplateDownloadView.as_view(), name='xls-template'),
    path('uuids/', UUIDGeneratorView.as_view(), name='uuids-generate'),
]