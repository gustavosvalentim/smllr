from dataclasses import dataclass
from smllr.shorturls.models import User


@dataclass
class UserMetadata:
    ip_address: str
    user_agent: str
    device_type: str
    referrer: str
    user: User
    is_anonymous: bool = True
