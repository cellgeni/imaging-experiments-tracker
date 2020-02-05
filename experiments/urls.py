# urls.py
from django.urls import path
from experiments.views import MeasurementXLSImportView, XLSTemplateDownloadView, ColumnsXLSImportView

urlpatterns = [
    path('import/', MeasurementXLSImportView.as_view()),
    path('columns/', ColumnsXLSImportView.as_view()),
    path('xls-template/', XLSTemplateDownloadView.as_view(), name='xls-download'),
]