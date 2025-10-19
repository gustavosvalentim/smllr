from django.http import HttpRequest
from django.test import TestCase

from smllr.fingerprint.parser import HttpRequestFingerprintParser


class FingerprintTestCase(TestCase):
    """
    Test case for the Fingerprint model.
    This class can be extended to include more tests as needed.
    """

    def test_fingerprint_creation(self):
        """
        Test the creation of a fingerprint instance.
        """

        request = HttpRequest()

        expects_ip_address = "192.168.1.86"
        expects_browser_name = "Firefox"
        expects_browser_version = "139.0"
        expects_os_name = "Windows"

        request.META["HTTP_USER_AGENT"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0"
        )
        request.META["HTTP_X_FORWARDED_FOR"] = expects_ip_address

        parser = HttpRequestFingerprintParser(request)
        fingerprint = parser.parse()

        assert fingerprint is not None, "Fingerprint should be created successfully"
        assert fingerprint.fingerprint_data.get("ip_address") == expects_ip_address, (
            f"IP address should be '{expects_ip_address}'"
        )
        assert (
            fingerprint.fingerprint_data.get("browser_name") == expects_browser_name
        ), f"Browser name should be '{expects_browser_name}'"
        assert (
            fingerprint.fingerprint_data.get("browser_version")
            == expects_browser_version
        ), f"Browser version should be '{expects_browser_version}'"
        assert fingerprint.fingerprint_data.get("os") == expects_os_name, (
            f"OS name should be '{expects_os_name}'"
        )
