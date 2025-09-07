from typing import Any

from django.http import HttpRequest
import httpagentparser


class HttpRequestFingerprintParser:
    """
    A class to represent a request fingerprint.
    This can be extended to include more fields as needed.
    """

    def __init__(self, request: HttpRequest):
        """
        Initializes the HttpRequestFingerprintParser with a Django HttpRequest object.
        """
        self.request = request

    def get_ip_address(self) -> str:
        """
        Helper method to extract the IP address from the request.
        """
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR', '')

    def parse(self) -> dict[str, Any]:
        """
        Creates a fingerprint based on the request data.
        This method should be implemented to extract relevant data from the request.
        """

        user_agent = httpagentparser.detect(self.request.META.get('HTTP_USER_AGENT', ''))

        return {
            'ip_address': self.get_ip_address(),
            'user_agent': self.request.META.get('HTTP_USER_AGENT', 'Unknown'),
            'browser_name': user_agent.get('browser', {}).get('name', 'Unknown'),
            'browser_version': user_agent.get('browser', {}).get('version', 'Unknown'),
            'os': user_agent.get('os', {}).get('name', 'Unknown'),
            'device_type': user_agent.get('dist', {}).get('name', 'Unknown'),
            'referrer': self.request.META.get('HTTP_REFERER', 'Unknown'),
        }
