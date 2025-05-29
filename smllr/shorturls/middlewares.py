from allauth.socialaccount.models import SocialAccount
from django.http import HttpRequest
from smllr.shorturls.helpers import get_device_type, get_ip_address
from smllr.shorturls.users import UserMetadata


class UserMetadataMiddleware:
    """
    Middleware to add user metadata to the request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        # This should use authentication or session data instead of just an IP address.
        ip_address = get_ip_address(request)
        request.user_metadata = UserMetadata(
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            device_type=get_device_type(request),
            referrer=request.META.get('HTTP_REFERER', ''),
            user=request.user,
            is_anonymous=request.user.is_anonymous,
        )

        return self.get_response(request)
