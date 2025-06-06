from django.conf import settings
from django.http import HttpRequest, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import FormView
from smllr.shorturls.forms import ShortURLForm
from smllr.shorturls.helpers import generate_short_code
from smllr.shorturls.models import ShortURL, ShortURLClick, User


class ShortURLView(View):

    def __store_analytics_data(self, request: HttpRequest, short_url: ShortURL):
        short_url.increment_clicks()
        short_url_click = ShortURLClick.objects.create(
            short_url=short_url,
            user_agent=request.user_metadata.user_agent,
            ip_address=request.user_metadata.ip_address,
            device_type=request.user_metadata.device_type,
            referrer=request.user_metadata.referrer,
        )
        short_url_click.save()

    def get(self, request: HttpRequest, short_code: str):
        """
        Redirects to the original URL based on the short code provided in the request.
        """

        short_url = ShortURL.objects.filter(short_code=short_code).first()

        if not short_url:
            return HttpResponseNotFound("Short URL was not found.")
        
        self.__store_analytics_data(request, short_url)

        return redirect(short_url.destination_url)


class ShortURLFormView(FormView):
    """
    View to handle the creation of short URLs.
    """

    template_name = 'smllr/shorturls.html'
    form_class = ShortURLForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.pk is not None:
            context['shorturls_list'] = ShortURL.objects.filter(user=self.request.user_metadata.user).order_by('-created_at')
        else:
            context['shorturls_list'] = ShortURL.objects.filter(user__ip_address=self.request.user_metadata.ip_address).order_by('-created_at')

        return context

    def form_valid(self, form: ShortURLForm, **kwargs):
        """
        If the form is valid, save the short URL and redirect to the success URL.
        """

        user = self.request.user_metadata.user
        if user.pk is None:
            # Create a new user if one does not exist
            user = User.objects.create(
                username=self.request.user_metadata.ip_address,
                ip_address=self.request.user_metadata.ip_address,
                name='Anonymous',
                is_anonymous=True,
            )
            user.save()

        if ShortURL.objects.filter(user=user).count() >= settings.MAX_SHORTURLS_PER_ANON_USER:
            # Limit the number of short URLs per user
            form.add_error(None, f"You have reached the limit of {settings.MAX_SHORTURLS_PER_ANON_USER} URLs.")
            return self.form_invalid(form)

        if not form.cleaned_data['short_code'] or form.cleaned_data['short_code'].strip() == '':
            # Generate a short code if not provided
            form.cleaned_data['short_code'] = generate_short_code()

        short_url = ShortURL.objects.create(
            user=user,
            destination_url=form.cleaned_data['destination_url'],
            short_code=form.cleaned_data['short_code'],
        )
        short_url.save()

        return super().form_valid(form)


class ShortURLAnalyticsView(View):
    """
    View to handle the analytics of short URLs.
    """

    def get(self, request: HttpRequest, short_code: str):
        """
        Returns the analytics data for the short URL based on the short code provided in the request.
        """

        short_url = ShortURL.objects.filter(short_code=short_code).first()
        clicks = ShortURLClick.objects.filter(short_url=short_url).order_by('-clicked_at')

        if not short_url:
            return HttpResponseNotFound("Short URL was not found.")
        
        context = {
            'shorturl': short_url,
            'latest_clicks': clicks[:10],
            'desktop_clicks': clicks.filter(device_type='Desktop').count(),
            'mobile_clicks': clicks.filter(device_type='Mobile').count(),
            'tablet_clicks': clicks.filter(device_type='Tablet').count(),
            'total_clicks': clicks.count(),
        }

        return render(request, 'smllr/analytics.html', context)
