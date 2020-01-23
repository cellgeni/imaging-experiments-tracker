# urls.py
from django.urls import path
from experiments.views import MeasurementXLSImportView, XLSTemplateDownloadView

urlpatterns = [
    path('import/', MeasurementXLSImportView.as_view()),
    path('xls-template/', XLSTemplateDownloadView.as_view()),
]