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
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return self.request.META.get("REMOTE_ADDR", "")

    def parse(self) -> dict[str, Any]:
        """
        Creates a fingerprint based on the request data.
        This method should be implemented to extract relevant data from the request.
        """

        user_agent = httpagentparser.detect(
            self.request.META.get("HTTP_USER_AGENT", "")
        )

        # Determine device type
        # Mobile devices have 'dist' key (iPhone, Android, iPad)
        # Desktop devices don't have 'dist', use platform info instead
        device_type = None
        if "dist" in user_agent:
            dist_name = user_agent["dist"].get("name", "")
            if dist_name:
                dist_name_lower = dist_name.lower()
                if "iphone" in dist_name_lower:
                    device_type = "Mobile"
                elif "ipad" in dist_name_lower:
                    device_type = "Tablet"
                elif "android" in dist_name_lower:
                    device_type = "Mobile"
                else:
                    device_type = dist_name
        else:
            # Desktop devices - check platform
            platform = user_agent.get("platform", {}).get("name", "")
            if platform:
                device_type = "Desktop"

        return {
            "ip_address": self.get_ip_address(),
            "user_agent": self.request.META.get("HTTP_USER_AGENT", ""),
            "browser_name": user_agent.get("browser", {}).get("name"),
            "browser_version": user_agent.get("browser", {}).get("version"),
            "os": user_agent.get("os", {}).get("name"),
            "device_type": device_type,
            "referrer": self.request.META.get("HTTP_REFERER", ""),
        }
