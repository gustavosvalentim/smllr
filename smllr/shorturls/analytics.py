from django.http import HttpRequest


class RequestMetrics:
    ip_address: str = ''
    user_agent: str = ''
    device_type: str = ''
    referrer: str = ''

    def __get_ip_address(self, request: HttpRequest) -> str:
        """
        Helper method to extract the IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR', '')

    def __get_device_type(self, request: HttpRequest) -> str:
        """
        Helper method to determine the device type from the user agent.
        This can be extended to include more sophisticated device detection.
        """
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'Mobile' in user_agent:
            return 'Mobile'
        elif 'Tablet' in user_agent:
            return 'Tablet'
        else:
            return 'Desktop'

    @staticmethod
    def from_request(request: HttpRequest):
        """
        Factory method to create a RequestMetrics instance from an HttpRequest.
        """

        metrics = RequestMetrics()
        metrics.ip_address = metrics.__get_ip_address(request)
        metrics.user_agent = request.META.get('HTTP_USER_AGENT', '')
        metrics.device_type = metrics.__get_device_type(request)
        metrics.referrer = request.META.get('HTTP_REFERER', '')

        return metrics
