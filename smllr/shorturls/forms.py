from django import forms
from smllr.shorturls.models import ShortURL


class ShortURLForm(forms.ModelForm):
    """
    Form for creating or updating a short URL.
    This form is based on the ShortURL model.
    """

    short_code = forms.URLField(required=False)

    class Meta:
        model = ShortURL
        fields = ['destination_url', 'short_code']
