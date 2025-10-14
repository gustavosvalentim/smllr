import logging

from django.db import transaction
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.views.generic import FormView, View

from smllr.core.response import forbidden, not_found
from smllr.shorturls.forms import ShortURLForm
from smllr.shorturls.models import ShortURL, ShortURLClick, User
from smllr.users.mixins import NonAnonymousUserRequiredMixin


class ShortURLRedirectView(View):

    @transaction.atomic
    def get(self, request: HttpRequest, short_code: str):
        """
        Redirects to the original URL based on the short code provided in the request.
        """

        logger = logging.getLogger(self.__class__.__name__)
        short_url = ShortURL.objects.filter(short_code=short_code).first()

        if short_url is None or short_url.is_expired():
            return not_found(request, "Short URL not found or has expired.")
        
        try:
            # TODO: message queue?
            # saving fingerprint and increment a click on a queue is better than on a view.
            # this view should be pretty fast, so get the URL and redirect as fast as possible.
            # if there is an error saving the fingerprint, we don't care for now,
            # throw it in a queue and handle it later
            request.fingerprint.save()
            short_url.increment_clicks()
            short_url_click = ShortURLClick.objects.create(
                short_url=short_url,
                fingerprint=request.fingerprint,
            )
            short_url_click.save()
        except Exception as err:
            logger.error("Error saving request fingerprint", err, exc_info=True)

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
            user_ip_address = self.request.fingerprint.ip_address
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

        logger = logging.getLogger(self.__class__.__name__)
        user = self.request.user
        try:
            if user.pk is None:
                user_ip_address = self.request.fingerprint.ip_address
                queryset = User.objects.filter(ip_address=user_ip_address, is_anonymous=True)

                if queryset.exists():
                    user = queryset.first()
                else:
                    user = User.objects.create_anonymous(user_ip_address)

            ShortURL.objects.create(
                user=user,
                destination_url=form.cleaned_data['destination_url'],
                name=form.cleaned_data['name'],
                short_code=form.cleaned_data['short_code']
            )
        except Exception as ex:
            logger.error("Error creating short URL", ex, exc_info=True)
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

        short_url = ShortURL.objects.filter(short_code=short_code).first()

        if not short_url:
            return not_found(self.request)

        if short_url.user.pk != self.request.user.pk:
            return forbidden(self.request)
 
        context = {
            'shorturl': short_url,
        }

        return render(request, 'smllr/shorturl_details.html', context)
