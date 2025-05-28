import string, random

from django.http import HttpRequest


def generate_short_code(length: int = 10) -> str:
    """
    Generates a random short URL slug of the specified length.
    
    :param length: Length of the generated slug. Default is 10 characters.
    :return: A random string of the specified length consisting of alphanumeric characters.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


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
