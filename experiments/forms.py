from django import forms


class XLSUploadForm(forms.Form):
    file = forms.FileField()


class UUIDGeneratorForm(forms.Form):
    quantity = forms.IntegerField(label='', max_value=1000)
