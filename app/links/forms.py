from django import forms


class UrlsForm(forms.Form):
    redirect_url = forms.URLField()
    is_private = forms.BooleanField(required=False)


class UrlsPatchForm(forms.Form):
    redirect_url = forms.URLField(required=False)
    is_private = forms.BooleanField(required=False)