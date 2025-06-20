from django.http import HttpRequest

from smllr.shorturls.tracking import get_user_metadata


class UserMetadataMiddleware:
    """
    Middleware to add user metadata to the request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        # This should use authentication or session data instead of just an IP address.
        request.user_metadata = get_user_metadata(request)
        return self.get_response(request)
