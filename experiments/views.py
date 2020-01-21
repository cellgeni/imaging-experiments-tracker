from django import forms
from django.shortcuts import render
from django.views import View


class XLSUploadForm(forms.Form):
    file = forms.FileField()


class MeasurementXLSImportView(View):

    def get(self, request, *args, **kwargs):
        form = XLSUploadForm()
        return render(request, 'xls.html', {'form': form})

    def _write_file(self, f):
        with open('name.xls', 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def handle_uploaded_file(self, f):
        self._write_file(f)
        return "some date"

    def post(self,  request, *args, **kwargs):
        form = XLSUploadForm(request.POST, request.FILES)
        if form.is_valid():
            data = self.handle_uploaded_file(request.FILES['file'])
        else:
            data = "form invalid"
        return render(request, 'xls.html', {'form': form,
                                            'data': data})
