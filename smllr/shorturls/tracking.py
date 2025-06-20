from dataclasses import dataclass

from django.http import HttpRequest
from smllr.shorturls.models import User


@dataclass
class UserMetadata:
    ip_address: str
    user_agent: str
    device_type: str
    referrer: str
    user: User
    is_anonymous: bool = True


def get_ip_address(request: HttpRequest) -> str:
        """
        Helper method to extract the IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR', '')


def get_device_type(request: HttpRequest) -> str:
    """
    Helper method to determine the device type from the user agent.
    This can be extended to include more sophisticated device detection.
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if 'mobile' in user_agent:
        return 'Mobile'
    elif 'tablet' in user_agent:
        return 'Tablet'
    else:
        return 'Desktop'


def get_user_metadata(request: HttpRequest) -> UserMetadata:
    return UserMetadata(
        ip_address=get_ip_address(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        device_type=get_device_type(request),
        referrer=request.META.get('HTTP_REFERER', ''),
        user=request.user,
        is_anonymous=request.user.is_anonymous,
    )
