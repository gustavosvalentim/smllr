from django.http import HttpRequest

from smllr.fingerprint.models import Fingerprint
from smllr.fingerprint.parser import HttpRequestFingerprintParser

class RequestFingerprintMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """
        Middleware to get request fingerprint and attach it to the request object.
        """

        parser = HttpRequestFingerprintParser(request)
        fingerprint = parser.parse()
        request.fingerprint = Fingerprint(fingerprint_data=fingerprint)

        return self.get_response(request)
