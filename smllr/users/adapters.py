from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect

from smllr.users.models import User


class AccountAdapter(DefaultAccountAdapter):
    def authentication_error(
        self, request, provider_id, error, exception, extra_context
    ):
        print(
            "SocialAccount authentication error!",
            "error",
            request,
            {
                "provider_id": provider_id,
                "error": error.__str__(),
                "exception": exception.__str__(),
                "extra_context": extra_context,
            },
        )

    def is_open_for_signup(self, request):
        return False

    def respond_user_inactive(self, request, user):
        return redirect("/")


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def authentication_error(
        self, request, provider_id, error, exception, extra_context
    ):
        print(
            "SocialAccount authentication error!",
            "error",
            request,
            {
                "provider_id": provider_id,
                "error": error.__str__(),
                "exception": exception.__str__(),
                "extra_context": extra_context,
            },
        )

    def get_connect_redirect_url(self, request, socialaccount):
        """
        Override the redirect URL after a successful social account connection.
        """
        return "/"

    def is_open_for_signup(self, login, email):
        return True

    def pre_social_login(self, request, sociallogin):
        user = User.objects.filter(email=sociallogin.user.email).first()
        if user and not sociallogin.is_existing:
            sociallogin.connect(request, user)

    def save_user(self, request, sociallogin, form=None):
        """
        Override save user by bypassing form.
        """

        user = sociallogin.user
        user.ip_address = request.fingerprint.fingerprint_data.get("ip_address")
        user.is_guest_user = False
        user.set_unusable_password()
        user.save()
        sociallogin.save(request)
        return user
