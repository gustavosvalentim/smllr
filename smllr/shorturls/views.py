import logging

from django.db import transaction
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.views.generic import FormView, View

from smllr.cache import RedisConnectionFactory, ShortURLCache
from smllr.core.response import forbidden, not_found
from smllr.shorturls.tasks import save_shorturl_click
from smllr.shorturls.forms import ShortURLForm
from smllr.shorturls.models import ShortURL, User
from smllr.subscriptions.mixins import ProSubscriptionRequiredMixin
from smllr.users.mixins import NonAnonymousUserRequiredMixin


class ShortURLRedirectView(View):
    cache = ShortURLCache(RedisConnectionFactory.get())

    @transaction.atomic
    def get(self, request: HttpRequest, short_code: str):
        """
        Redirects to the original URL based on the short code provided in the request.
        """

        logger = logging.getLogger(self.__class__.__name__)
        short_url = self.cache.get(short_code)

        if short_url is None:
            short_url = ShortURL.objects.filter(short_code=short_code).first()

            logger.debug(f"Cache miss for {short_code}")

            if short_url is not None and not short_url.is_expired():
                self.cache.set(
                    code=short_url.short_code,
                    url=short_url.destination_url,
                    created_at=short_url.created_at,
                    user_id=short_url.user.pk,
                )

        if short_url is None or short_url.is_expired():
            return not_found(request, "Short URL not found or has expired.")

        try:
            request.fingerprint.save()
            save_shorturl_click.delay(short_code, request.fingerprint.pk)
        except Exception as err:
            logger.error("Error saving request fingerprint", err, exc_info=True)

        return redirect(short_url.destination_url)


class ShortURLFormView(FormView):
    """
    View to handle the creation of short URLs.
    """

    template_name = "smllr/shorturl_list.html"
    form_class = ShortURLForm
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get("page", 1)
        queryset = ShortURL.objects.order_by("-created_at")

        if self.request.user.is_anonymous:
            user_ip_address = self.request.fingerprint.ip_address
            queryset = queryset.filter(user__ip_address=user_ip_address, user__is_anonymous=True)
        else:
            queryset = queryset.filter(user=self.request.user, user__is_anonymous=False)

        paginator = Paginator(queryset, 10)

        context.update(
            {
                "paginator": paginator,
                "shorturls_list": paginator.get_page(page),
            }
        )

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
                    user = User.objects.create_anonymous(ip_address=user_ip_address)

            ShortURL.objects.create(
                user=user,
                destination_url=form.cleaned_data["destination_url"],
                name=form.cleaned_data["name"],
                short_code=form.cleaned_data["short_code"],
            )
        except Exception as ex:
            logger.error("Error creating short URL", ex, exc_info=True)
            form.add_error(None, ex)
            return self.form_invalid(form)

        return super().form_valid(form)


class ShortURLDetailsView(NonAnonymousUserRequiredMixin, ProSubscriptionRequiredMixin, View):
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
            "shorturl": short_url,
        }

        return render(request, "smllr/shorturl_details.html", context)
