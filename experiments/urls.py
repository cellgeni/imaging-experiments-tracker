from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from experiments.views import MeasurementXLSImportView, XLSTemplateDownloadView, WholeFileXLSImportView, \
    UUIDGeneratorView, UUIDAndCreateModeInjectorView



urlpatterns = [
    path('', TemplateView.as_view(template_name="home.html"), name='home'),
    path('import/', MeasurementXLSImportView.as_view(), name='upload-xls'),
    path('columns/', WholeFileXLSImportView.as_view()),
    path('inject-uuids/', UUIDAndCreateModeInjectorView.as_view()),
    path('xls-template/', XLSTemplateDownloadView.as_view(), name='xls-template'),
    path('uuids/', UUIDGeneratorView.as_view(), name='uuids-generate'),
]

for u in urlpatterns:
    u.callback = login_required(u.callback) 
    
