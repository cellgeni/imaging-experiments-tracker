# urls.py
from django.urls import path
from experiments.views import MeasurementXLSImportView

urlpatterns = [
    path('import/', MeasurementXLSImportView.as_view()),
]