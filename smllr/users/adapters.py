from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect

from smllr.shorturls.tracking import get_ip_address


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False

    def respond_user_inactive(self, request, user):
        return redirect('/')


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, socialaccount):
        """
        Override the redirect URL after a successful social account connection.
        """
        return '/'

    def is_open_for_signup(self, login, email):
        return True

    def save_user(self, request, sociallogin, form=None):
        """
        Override save user by bypassing form.
        """

        user = sociallogin.user
        user.username = user.email
        user.ip_address = get_ip_address(request)
        user.is_anonymous = False
        user.set_unusable_password()
        user.save()
        sociallogin.save(request)
        return user
