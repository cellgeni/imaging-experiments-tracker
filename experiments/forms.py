from django import forms


class XLSUploadForm(forms.Form):
    file = forms.FileField()
