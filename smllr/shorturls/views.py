import json

from django.db import transaction
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import FormView, View

from smllr.core.response import forbidden, not_found
from smllr.shorturls.forms import ShortURLForm
from smllr.shorturls.models import ShortURL, ShortURLClick, User
from smllr.users.mixins import NonAnonymousUserRequiredMixin


class ShortURLView(View):

    def get(self, request: HttpRequest, short_code: str):
        """
        Redirects to the original URL based on the short code provided in the request.
        """

        short_url = ShortURL.objects.filter(short_code=short_code).first()

        if short_url is None or short_url.is_expired():
            return not_found(request, "Short URL not found or has expired.")
        
        short_url.increment_clicks()

        short_url_click = ShortURLClick.objects.create(
            short_url=short_url,
            user_agent=request.fingerprint.fingerprint_data.get('user_agent'),
            ip_address=request.fingerprint.fingerprint_data.get('ip_address'),
            device_type=request.fingerprint.fingerprint_data.get('device_type'),
            referrer=request.fingerprint.fingerprint_data.get('referrer'),
        )
        request.fingerprint.save()
        short_url_click.save()

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

        if self.request.user.is_anonymous:
            user_ip_address = self.request.fingerprint.fingerprint_data.get("ip_address")
            queryset = queryset.filter(user__ip_address=user_ip_address, user__is_anonymous=True)
        else:
            queryset = queryset.filter(user=self.request.user, user__is_anonymous=False)

        paginator = Paginator(queryset, 10)

        context.update({
            'paginator': paginator,
            'shorturls_list': paginator.get_page(page),
        })

        return context

    @transaction.atomic
    def form_valid(self, form: ShortURLForm, **kwargs):
        """
        If the form is valid, save the short URL and redirect to the success URL.
        """

        user = self.request.user
        if user.pk is None:
            user_ip_address = self.request.fingerprint.fingerprint_data.get('ip_address')
            # Create a new user if one does not exist
            (user, _) = User.objects.get_or_create(
                username=user_ip_address,
                ip_address=user_ip_address,
                name='Anonymous',
                is_anonymous=True,
            )

        try:
            ShortURL.objects.create(
                user=user,
                destination_url=form.cleaned_data['destination_url'],
                name=form.cleaned_data['name'],
                short_code=form.cleaned_data['short_code']
            )
        except Exception as ex:
            form.add_error(None, ex)
            return self.form_invalid(form)

        return super().form_valid(form)


class ShortURLDetailsView(NonAnonymousUserRequiredMixin, View):
    """
    View to handle the analytics of short URLs.
    """

    def get(self, request: HttpRequest, short_code: str):
        """
        Returns the analytics data for the short URL based on the short code provided in the request.
        """

        if short_code is None:
            return not_found(self.request)

        short_url = ShortURL.objects.filter(short_code=short_code).first()

        if short_url.user.pk != self.request.user.pk:
            return forbidden(self.request)

        clicks = ShortURLClick.objects.filter(short_url=short_url).order_by('-clicked_at')

        if not short_url:
            return not_found(self.request)
        
        context = {
            'shorturl': short_url,
            'latest_clicks': clicks[:10],
            'desktop_clicks': clicks.filter(device_type='Desktop').count(),
            'mobile_clicks': clicks.filter(device_type='Mobile').count(),
            'tablet_clicks': clicks.filter(device_type='Tablet').count(),
            'total_clicks': clicks.count(),
        }

        return render(request, 'smllr/shorturl_details.html', context)


class AnalyticsAPIView(NonAnonymousUserRequiredMixin, View):

    def get(self, request: HttpRequest, short_code: str):
        if short_code is None:
            return not_found(self.request)

        short_url = ShortURL.objects.filter(short_code=short_code).first()
        clicks = ShortURLClick.objects.filter(short_url=short_url).order_by('-clicked_at')

        if not short_url:
            return not_found(self.request)
        
        latest_clicks = []
        for click in clicks[:10]:
            latest_clicks.append({
                'clicked_at': click.clicked_at.isoformat(),
                'user_agent': click.user_agent,
                'ip_address': click.ip_address,
                'device_type': click.device_type,
                'referrer': click.referrer,
            })

        string_response = json.dumps({
            'latest_clicks': latest_clicks,
            'desktop_clicks': clicks.filter(device_type='Desktop').count(),
            'mobile_clicks': clicks.filter(device_type='Mobile').count(),
            'tablet_clicks': clicks.filter(device_type='Tablet').count(),
            'total_clicks': clicks.count(),
        })

        response = HttpResponse()
        response.status_code = 200
        response.content = string_response
        response['Content-Type'] = 'application/json'

        return response
