from django.http import HttpRequest, HttpResponseNotFound
from django.shortcuts import redirect
from django.views import View
from django.views.generic import FormView
from smllr.shorturls.forms import ShortURLForm
from smllr.shorturls.generator import generate_short_code
from smllr.shorturls.models import ShortURL


class ShortURLView(View):
    """
    Base view for handling short URLs.
    This can be extended to implement specific functionalities like creating,
    retrieving, or redirecting short URLs.
    """

    def get(self, _: HttpRequest, short_code: str):
        """
        Redirects to the original URL based on the short code provided in the request.
        """

        short_url = ShortURL.objects.filter(short_code=short_code).first()

        if not short_url:
            return HttpResponseNotFound("Short URL was not found.")

        short_url.increment_clicks()

        return redirect(short_url.original_url)


class ShortURLFormView(FormView):
    """
    View to handle the creation of short URLs.
    """

    template_name = 'smllr/shorturls.html'
    form_class = ShortURLForm
    success_url = '/admin/short-urls'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shorturls_list'] = ShortURL.objects.all().order_by('-created_at')
        return context

    def form_valid(self, form: ShortURLForm):
        """
        If the form is valid, save the short URL and redirect to the success URL.
        """

        if not form.cleaned_data['short_code'] or form.cleaned_data['short_code'].strip() == '':
            # Generate a short code if not provided
            form.cleaned_data['short_code'] = generate_short_code()

        short_url = ShortURL.objects.create(
            destination_url=form.cleaned_data['destination_url'],
            short_code=form.cleaned_data['short_code'],
        )
        short_url.save()

        return super().form_valid(form)
