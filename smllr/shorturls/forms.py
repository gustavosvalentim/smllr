from django import forms


class ShortURLForm(forms.Form):
    """
    Form for creating or updating a short URL.
    This form is based on the ShortURL model.
    """

    destination_url = forms.URLField()
    name = forms.CharField(max_length=150, required=False)
    short_code = forms.CharField(max_length=50, required=False)
