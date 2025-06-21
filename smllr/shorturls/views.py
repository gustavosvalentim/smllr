from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView, View
from smllr.core.response import not_found
from smllr.shorturls.forms import ShortURLForm
from smllr.shorturls.helpers import generate_short_code
from smllr.shorturls.models import ShortURL, ShortURLClick, User
from smllr.users.mixins import NonAnonymousUserRequiredMixin


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

        if short_url is None or short_url.is_expired(settings.SHORTURL_EXPIRATION_TIME_DAYS):
            return not_found(request, "Short URL not found or has expired.")

        self.__store_analytics_data(self.request, short_url)

        return redirect(short_url.destination_url)


class ShortURLFormView(FormView):
    """
    View to handle the creation of short URLs.
    """

    template_name = 'smllr/shorturl_list.html'
    form_class = ShortURLForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        queryset = ShortURL.objects.order_by('-created_at')

        if not self.request.user.is_anonymous:
            queryset = queryset.filter(user=self.request.user_metadata.user, user__is_anonymous=False)
        else:
            queryset = queryset.filter(user__ip_address=self.request.user_metadata.ip_address, user__is_anonymous=True)

        paginator = Paginator(queryset, 10)
        context['paginator'] = paginator
        context['shorturls_list'] = paginator.get_page(page)

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

        short_code = form.cleaned_data.get('short_code', '').strip()

        if short_code == '':
            # Generate a short code if not provided
            form.cleaned_data['short_code'] = generate_short_code()

        short_url = ShortURL.objects.create(
            user=user,
            destination_url=form.cleaned_data['destination_url'],
            short_code=form.cleaned_data['short_code'],
        )
        short_url.save()

        return super().form_valid(form)


class ShortURLDetailsView(NonAnonymousUserRequiredMixin, TemplateView):
    """
    View to handle the analytics of short URLs.
    """

    template_name = 'smllr/shorturl_details.html'

    def get_context_data(self, *args, **kwargs):
        """
        Returns the analytics data for the short URL based on the short code provided in the request.
        """

        context = super().get_context_data(*args, **kwargs)

        short_code = self.kwargs.get('short_code', None)

        if short_code is None:
            return not_found(self.request)

        short_url = ShortURL.objects.filter(short_code=short_code).first()
        clicks = ShortURLClick.objects.filter(short_url=short_url).order_by('-clicked_at')

        if not short_url:
            return not_found(self.request)
        
        context.update({
            'shorturl': short_url,
            'latest_clicks': clicks[:10],
            'desktop_clicks': clicks.filter(device_type='Desktop').count(),
            'mobile_clicks': clicks.filter(device_type='Mobile').count(),
            'tablet_clicks': clicks.filter(device_type='Tablet').count(),
            'total_clicks': clicks.count(),
        })

        return context
