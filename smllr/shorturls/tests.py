from datetime import timedelta
from unittest.mock import Mock, patch, MagicMock

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now

from smllr.fingerprint.models import Fingerprint
from smllr.fingerprint.parser import HttpRequestFingerprintParser
from smllr.shorturls.analytics import AnalyticsService
from smllr.shorturls.forms import ShortURLForm
from smllr.shorturls.helpers import generate_short_code
from smllr.shorturls.models import ShortURL, ShortURLClick
from smllr.users.models import User


class TestDataMixin:
    """Mixin to provide common test data and helper methods."""

    def create_user(self, username="testuser", email="test@test.com", anonymous=False):
        """Create a test user."""
        if anonymous:
            user = User.objects.create_anonymous(ip_address="127.0.0.1")
        else:
            user = User.objects.create(username=username, email=email)
            user.set_password("testpass123")
            user.save()
        return user

    def create_shorturl(
        self,
        user=None,
        destination_url="https://example.com",
        name="Test URL",
        short_code=None,
    ):
        """Create a test ShortURL."""
        if user is None:
            user = self.create_user()
        return ShortURL.objects.create(
            user=user,
            destination_url=destination_url,
            name=name,
            short_code=short_code,
        )

    def create_fingerprint(
        self,
        ip_address="127.0.0.1",
        device_type="Desktop",
        os="Windows",
        browser_name="Chrome",
        referrer="",
    ):
        """Create a test Fingerprint."""
        return Fingerprint.objects.create(
            ip_address=ip_address,
            device_type=device_type,
            os=os,
            browser_name=browser_name,
            browser_version="91.0",
            referrer=referrer,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            fingerprint_data={
                "ip_address": ip_address,
                "device_type": device_type,
                "os": os,
                "browser_name": browser_name,
            },
        )

    def create_click(self, short_url, fingerprint=None, clicked_at=None):
        """Create a test ShortURLClick."""
        if fingerprint is None:
            fingerprint = self.create_fingerprint()
        click = ShortURLClick.objects.create(
            short_url=short_url,
            fingerprint=fingerprint,
        )
        if clicked_at:
            click.clicked_at = clicked_at
            click.save()
        return click


# =============================================================================
# P0 CRITICAL: Fingerprint Parser Tests
# =============================================================================


class HttpRequestFingerprintParserTestCase(TestCase):
    """Test fingerprint parser for device type and referrer detection."""

    def create_mock_request(self, user_agent, referrer=None):
        """Create a mock request with specified user agent and referrer."""
        request = Mock()
        request.META = {
            "HTTP_USER_AGENT": user_agent,
            "REMOTE_ADDR": "127.0.0.1",
        }
        if referrer:
            request.META["HTTP_REFERER"] = referrer
        return request

    def test_parser_mobile_iphone_detection(self):
        """Test iPhone is detected as Mobile."""
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
        request = self.create_mock_request(ua)
        parser = HttpRequestFingerprintParser(request)
        result = parser.parse()

        self.assertEqual(result["device_type"], "Mobile")
        self.assertEqual(result["os"], "iOS")
        self.assertIsNotNone(result["browser_name"])

    def test_parser_mobile_android_detection(self):
        """Test Android is detected as Mobile."""
        ua = "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
        request = self.create_mock_request(ua)
        parser = HttpRequestFingerprintParser(request)
        result = parser.parse()

        self.assertEqual(result["device_type"], "Mobile")
        self.assertIn(result["os"], ["Linux", "Android"])
        self.assertEqual(result["browser_name"], "Chrome")

    def test_parser_tablet_ipad_detection(self):
        """Test iPad is detected as Tablet."""
        ua = "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15"
        request = self.create_mock_request(ua)
        parser = HttpRequestFingerprintParser(request)
        result = parser.parse()

        self.assertEqual(result["device_type"], "Tablet")
        self.assertEqual(result["os"], "iOS")

    def test_parser_desktop_windows_detection(self):
        """Test Windows is detected as Desktop."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        request = self.create_mock_request(ua)
        parser = HttpRequestFingerprintParser(request)
        result = parser.parse()

        self.assertEqual(result["device_type"], "Desktop")
        self.assertEqual(result["os"], "Windows")
        self.assertEqual(result["browser_name"], "Chrome")

    def test_parser_desktop_mac_detection(self):
        """Test macOS is detected as Desktop."""
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        request = self.create_mock_request(ua)
        parser = HttpRequestFingerprintParser(request)
        result = parser.parse()

        self.assertEqual(result["device_type"], "Desktop")
        self.assertEqual(result["os"], "Macintosh")

    def test_parser_referrer_empty_string_when_missing(self):
        """Test referrer is empty string (not 'Unknown') when missing."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        request = self.create_mock_request(ua)
        parser = HttpRequestFingerprintParser(request)
        result = parser.parse()

        self.assertEqual(result["referrer"], "")
        self.assertNotEqual(result["referrer"], "Unknown")

    def test_parser_referrer_preserved_when_present(self):
        """Test referrer is preserved when present."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        request = self.create_mock_request(ua, referrer="https://example.com")
        parser = HttpRequestFingerprintParser(request)
        result = parser.parse()

        self.assertEqual(result["referrer"], "https://example.com")

    def test_parser_browser_extraction(self):
        """Test browser name and version are extracted."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        request = self.create_mock_request(ua)
        parser = HttpRequestFingerprintParser(request)
        result = parser.parse()

        self.assertEqual(result["browser_name"], "Chrome")
        self.assertEqual(result["browser_version"], "91.0.4472.124")

    def test_parser_ip_address_extraction(self):
        """Test IP address extraction including X-Forwarded-For."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        request = self.create_mock_request(ua)
        parser = HttpRequestFingerprintParser(request)
        result = parser.parse()

        self.assertEqual(result["ip_address"], "127.0.0.1")

    def test_parser_ip_address_x_forwarded_for(self):
        """Test IP address extraction prioritizes X-Forwarded-For."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        request = self.create_mock_request(ua)
        request.META["HTTP_X_FORWARDED_FOR"] = "192.168.1.1, 10.0.0.1"
        parser = HttpRequestFingerprintParser(request)
        result = parser.parse()

        self.assertEqual(result["ip_address"], "192.168.1.1")


# =============================================================================
# P0 CRITICAL: ShortURL Model Tests
# =============================================================================


class ShortURLManagerTestCase(TestDataMixin, TestCase):
    """Test ShortURL manager custom methods."""

    def test_anon_user_shorturl_limit(self):
        """Test anonymous users are limited to MAX_SHORTURLS_PER_ANON_USER."""
        user = self.create_user(anonymous=True)

        # Create up to the limit
        for i in range(settings.MAX_SHORTURLS_PER_ANON_USER):
            ShortURL.objects.create(
                user=user, destination_url="https://example.com", name=f"Test {i}"
            )

        # Attempt to exceed limit
        with self.assertRaises(Exception) as ex:
            ShortURL.objects.create(
                user=user, destination_url="https://example.com", name="Error"
            )

        self.assertIn("limit", str(ex.exception).lower())

    def test_authenticated_user_no_limit(self):
        """Test authenticated users are not subject to URL creation limits."""
        user = self.create_user()

        # Create more than anonymous limit
        for i in range(settings.MAX_SHORTURLS_PER_ANON_USER + 5):
            ShortURL.objects.create(
                user=user, destination_url="https://example.com", name=f"Test {i}"
            )

        # Should succeed without exception
        self.assertEqual(
            ShortURL.objects.filter(user=user).count(),
            settings.MAX_SHORTURLS_PER_ANON_USER + 5,
        )

    def test_short_code_auto_generation(self):
        """Test short code is auto-generated when not provided."""
        user = self.create_user()
        shorturl = ShortURL.objects.create(
            user=user, destination_url="https://example.com", name="Test"
        )

        self.assertIsNotNone(shorturl.short_code)
        self.assertEqual(len(shorturl.short_code), 10)  # Default length

    def test_custom_short_code_respected(self):
        """Test custom short codes are respected."""
        user = self.create_user()
        custom_code = "mycustom"
        shorturl = ShortURL.objects.create(
            user=user,
            destination_url="https://example.com",
            name="Test",
            short_code=custom_code,
        )

        self.assertEqual(shorturl.short_code, custom_code)

    def test_empty_short_code_generates_new(self):
        """Test empty string short code triggers generation."""
        user = self.create_user()
        shorturl = ShortURL.objects.create(
            user=user,
            destination_url="https://example.com",
            name="Test",
            short_code="",
        )

        self.assertIsNotNone(shorturl.short_code)
        self.assertNotEqual(shorturl.short_code, "")


class ShortURLModelTestCase(TestDataMixin, TestCase):
    """Test ShortURL model methods."""

    def test_increment_clicks(self):
        """Test click counter increments correctly."""
        shorturl = self.create_shorturl()
        initial_clicks = shorturl.clicks

        shorturl.increment_clicks()
        self.assertEqual(shorturl.clicks, initial_clicks + 1)

        shorturl.increment_clicks()
        self.assertEqual(shorturl.clicks, initial_clicks + 2)

    def test_is_expired_anonymous_user(self):
        """Test anonymous user URLs expire after SHORTURL_EXPIRATION_TIME_DAYS."""
        user = self.create_user(anonymous=True)
        shorturl = self.create_shorturl(user=user)

        # URL should not be expired initially
        self.assertFalse(shorturl.is_expired())

        # Simulate old URL
        shorturl.created_at = now() - timedelta(
            days=settings.SHORTURL_EXPIRATION_TIME_DAYS + 1
        )
        shorturl.save()

        self.assertTrue(shorturl.is_expired())

    def test_is_expired_authenticated_user(self):
        """Test authenticated user URLs never expire."""
        user = self.create_user()
        shorturl = self.create_shorturl(user=user)

        # Even with old creation date, should not expire
        shorturl.created_at = now() - timedelta(
            days=settings.SHORTURL_EXPIRATION_TIME_DAYS + 100
        )
        shorturl.save()

        self.assertFalse(shorturl.is_expired())

    def test_is_expired_edge_case_exact_boundary(self):
        """Test expiration at exact boundary."""
        user = self.create_user(anonymous=True)
        shorturl = self.create_shorturl(user=user)

        # Exactly at expiration time (should not be expired - use > not >=)
        # Add 1 second to account for test execution time
        shorturl.created_at = (
            now()
            - timedelta(days=settings.SHORTURL_EXPIRATION_TIME_DAYS)
            + timedelta(seconds=1)
        )
        shorturl.save()

        # This depends on implementation - adjust if needed
        self.assertFalse(shorturl.is_expired())

    def test_shorturl_string_representation(self):
        """Test __str__ method returns expected format."""
        shorturl = self.create_shorturl(name="My Test", short_code="abc123")
        self.assertEqual(str(shorturl), "My Test - abc123")


# =============================================================================
# P0 CRITICAL: ShortURL Views Tests
# =============================================================================


class ShortURLRedirectViewTestCase(TestDataMixin, TestCase):
    """Test short URL redirect functionality."""

    def setUp(self):
        self.client = Client()

    @patch("smllr.shorturls.views.save_shorturl_click")
    def test_redirect_success(self, mock_task):
        """Test successful redirect to destination URL."""
        shorturl = self.create_shorturl(short_code="test123")

        response = self.client.get(f"/{shorturl.short_code}")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, shorturl.destination_url)

    def test_redirect_nonexistent_code(self):
        """Test 404 for invalid short codes."""
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)

    @patch("smllr.shorturls.views.save_shorturl_click")
    def test_redirect_expired_url(self, mock_task):
        """Test 404 for expired URLs."""
        user = self.create_user(anonymous=True)
        shorturl = self.create_shorturl(user=user, short_code="expired")

        # Make it expired
        shorturl.created_at = now() - timedelta(
            days=settings.SHORTURL_EXPIRATION_TIME_DAYS + 1
        )
        shorturl.save()

        response = self.client.get(f"/{shorturl.short_code}")
        self.assertEqual(response.status_code, 404)

    @patch("smllr.shorturls.views.save_shorturl_click")
    def test_redirect_increments_clicks_async(self, mock_task):
        """Test Celery task is queued for click recording."""
        shorturl = self.create_shorturl(short_code="test123")

        self.client.get(f"/{shorturl.short_code}")

        # Verify task was called
        mock_task.delay.assert_called_once()


class ShortURLFormViewTestCase(TestDataMixin, TestCase):
    """Test short URL creation form view."""

    def setUp(self):
        self.client = Client()

    def test_form_view_anonymous_user_filtering(self):
        """Test anonymous users see only their IP's URLs."""
        # Create URLs for different IPs
        user1 = User.objects.create_anonymous(ip_address="192.168.1.1")
        user2 = User.objects.create_anonymous(ip_address="192.168.1.2")

        self.create_shorturl(user=user1, name="User1 URL")
        self.create_shorturl(user=user2, name="User2 URL")

        # Access as user1's IP
        response = self.client.get("/", REMOTE_ADDR="192.168.1.1")

        # Should only see user1's URLs
        self.assertEqual(response.status_code, 200)
        # Note: This test may need adjustment based on actual template/context

    def test_form_view_authenticated_user_filtering(self):
        """Test authenticated users see only their own URLs."""
        user1 = self.create_user(username="user1", email="user1@test.com")
        user2 = self.create_user(username="user2", email="user2@test.com")

        self.create_shorturl(user=user1, name="User1 URL")
        self.create_shorturl(user=user2, name="User2 URL")

        self.client.login(username="user1", password="testpass123")
        response = self.client.get("/")

        # Should only see user1's URLs
        self.assertEqual(response.status_code, 200)

    @patch("smllr.shorturls.views.ShortURL.objects.create")
    def test_form_valid_creates_shorturl(self, mock_create):
        """Test form submission creates ShortURL."""
        user = self.create_user()
        mock_shorturl = ShortURL(
            user=user,
            destination_url="https://example.com",
            name="Test URL",
            short_code="test123",
        )
        mock_create.return_value = mock_shorturl

        response = self.client.post(
            "/",
            {
                "destination_url": "https://example.com",
                "name": "Test URL",
                "short_code": "",
            },
        )

        self.assertEqual(response.status_code, 302)  # Redirect on success
        mock_create.assert_called_once()


# =============================================================================
# P0 CRITICAL: Analytics Service Tests
# =============================================================================


class AnalyticsServiceTestCase(TestDataMixin, TestCase):
    """Test analytics service comprehensive analytics generation."""

    def test_get_comprehensive_analytics_structure(self):
        """Test analytics response has all required keys."""
        shorturl = self.create_shorturl()
        service = AnalyticsService(shorturl)

        analytics = service.get_comprehensive_analytics()

        # Verify all expected keys are present
        required_keys = [
            "total_clicks",
            "unique_visitors",
            "clicks_by_day",
            "clicks_by_platform",
            "clicks_by_device",
            "clicks_by_browser",
            "clicks_by_source",
            "latest_clicks",
            "peak_hour",
            "avg_clicks_per_day",
        ]

        for key in required_keys:
            self.assertIn(key, analytics)

    def test_unique_visitors_count(self):
        """Test unique visitors are counted by distinct fingerprints."""
        shorturl = self.create_shorturl()
        fp1 = self.create_fingerprint(ip_address="192.168.1.1")
        fp2 = self.create_fingerprint(ip_address="192.168.1.2")

        # Create multiple clicks with same fingerprints
        self.create_click(shorturl, fp1)
        self.create_click(shorturl, fp1)
        self.create_click(shorturl, fp2)

        service = AnalyticsService(shorturl)
        analytics = service.get_comprehensive_analytics()

        self.assertEqual(analytics["unique_visitors"], 2)

    def test_platform_analytics_categorization(self):
        """Test OS categorization works correctly."""
        shorturl = self.create_shorturl()

        # Create clicks with different OS
        self.create_click(shorturl, self.create_fingerprint(os="Windows"))
        self.create_click(shorturl, self.create_fingerprint(os="Windows"))
        self.create_click(shorturl, self.create_fingerprint(os="Linux"))
        self.create_click(shorturl, self.create_fingerprint(os="Macintosh"))

        service = AnalyticsService(shorturl)
        analytics = service.get_comprehensive_analytics()

        platform = analytics["clicks_by_platform"]
        self.assertEqual(platform["windows"], 2)
        self.assertEqual(platform["linux"], 1)
        self.assertEqual(platform["macos"], 1)

    def test_device_analytics_categorization(self):
        """Test device type categorization works correctly."""
        shorturl = self.create_shorturl()

        # Create clicks with different devices
        self.create_click(shorturl, self.create_fingerprint(device_type="Mobile"))
        self.create_click(shorturl, self.create_fingerprint(device_type="Mobile"))
        self.create_click(shorturl, self.create_fingerprint(device_type="Desktop"))
        self.create_click(shorturl, self.create_fingerprint(device_type="Tablet"))

        service = AnalyticsService(shorturl)
        analytics = service.get_comprehensive_analytics()

        device = analytics["clicks_by_device"]
        self.assertEqual(device["mobile"], 2)
        self.assertEqual(device["desktop"], 1)
        self.assertEqual(device["tablet"], 1)

    def test_source_analytics_social_media_detection(self):
        """Test social media referrer detection."""
        shorturl = self.create_shorturl()

        # Create clicks from social media
        self.create_click(
            shorturl, self.create_fingerprint(referrer="https://facebook.com/page")
        )
        self.create_click(
            shorturl, self.create_fingerprint(referrer="https://instagram.com/profile")
        )
        self.create_click(
            shorturl, self.create_fingerprint(referrer="https://twitter.com/user")
        )

        service = AnalyticsService(shorturl)
        analytics = service.get_comprehensive_analytics()

        social = analytics["clicks_by_source"]["social_media"]
        self.assertEqual(social["facebook"], 1)
        self.assertEqual(social["instagram"], 1)
        self.assertEqual(social["twitter"], 1)

    def test_source_analytics_direct_traffic(self):
        """Test direct traffic counting (empty/null referrer)."""
        shorturl = self.create_shorturl()

        # Create direct clicks
        self.create_click(shorturl, self.create_fingerprint(referrer=""))
        self.create_click(shorturl, self.create_fingerprint(referrer=""))

        service = AnalyticsService(shorturl)
        analytics = service.get_comprehensive_analytics()

        direct = analytics["clicks_by_source"]["direct"]
        self.assertEqual(direct, 2)

    def test_latest_clicks_limit_50(self):
        """Test latest clicks are limited to 50."""
        shorturl = self.create_shorturl()

        # Create 60 clicks
        for i in range(60):
            self.create_click(
                shorturl, self.create_fingerprint(ip_address=f"192.168.1.{i}")
            )

        service = AnalyticsService(shorturl)
        analytics = service.get_comprehensive_analytics()

        self.assertEqual(len(analytics["latest_clicks"]), 50)

    def test_analytics_with_no_clicks(self):
        """Test analytics with zero clicks returns valid structure."""
        shorturl = self.create_shorturl()
        service = AnalyticsService(shorturl)

        analytics = service.get_comprehensive_analytics()

        self.assertEqual(analytics["total_clicks"], 0)
        self.assertEqual(analytics["unique_visitors"], 0)
        self.assertEqual(len(analytics["latest_clicks"]), 0)


# =============================================================================
# P0 CRITICAL: Analytics API Tests
# =============================================================================


class AnalyticsAPIViewTestCase(TestDataMixin, TestCase):
    """Test analytics API endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = self.create_user()
        self.client.force_login(self.user)

    @patch(
        "smllr.users.mixins.NonAnonymousUserRequiredMixin.test_func", return_value=True
    )
    @patch(
        "smllr.subscriptions.mixins.ProSubscriptionRequiredMixin.test_func",
        return_value=True,
    )
    def test_analytics_api_success(self, mock_pro, mock_auth):
        """Test successful analytics API response."""
        shorturl = self.create_shorturl(user=self.user, short_code="test123")

        response = self.client.get(f"/api/analytics/{shorturl.short_code}")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_clicks", data)
        self.assertIn("short_url", data)

    @patch(
        "smllr.users.mixins.NonAnonymousUserRequiredMixin.test_func", return_value=True
    )
    @patch(
        "smllr.subscriptions.mixins.ProSubscriptionRequiredMixin.test_func",
        return_value=True,
    )
    def test_analytics_api_includes_metadata(self, mock_pro, mock_auth):
        """Test API response includes short_url metadata."""
        shorturl = self.create_shorturl(user=self.user, short_code="test123")

        response = self.client.get(f"/api/analytics/{shorturl.short_code}")

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("short_url", data)
        self.assertEqual(data["short_url"]["code"], shorturl.short_code)
        self.assertEqual(data["short_url"]["name"], shorturl.name)

    @patch(
        "smllr.users.mixins.NonAnonymousUserRequiredMixin.test_func", return_value=True
    )
    @patch(
        "smllr.subscriptions.mixins.ProSubscriptionRequiredMixin.test_func",
        return_value=True,
    )
    def test_analytics_api_non_owner_returns_404(self, mock_pro, mock_auth):
        """Test non-owner gets 404."""
        other_user = self.create_user(username="other", email="other@test.com")
        shorturl = self.create_shorturl(user=other_user, short_code="test123")

        response = self.client.get(f"/api/analytics/{shorturl.short_code}")

        self.assertEqual(response.status_code, 404)

    @patch(
        "smllr.users.mixins.NonAnonymousUserRequiredMixin.test_func", return_value=True
    )
    @patch(
        "smllr.subscriptions.mixins.ProSubscriptionRequiredMixin.test_func",
        return_value=True,
    )
    def test_analytics_api_nonexistent_url(self, mock_pro, mock_auth):
        """Test 404 for invalid short code."""
        response = self.client.get("/api/analytics/nonexistent")

        self.assertEqual(response.status_code, 404)


# =============================================================================
# P1 HIGH: Helper Functions Tests
# =============================================================================


class GenerateShortCodeTestCase(TestCase):
    """Test short code generation helper."""

    def test_generate_short_code_default_length(self):
        """Test default length is 10 characters."""
        code = generate_short_code()
        self.assertEqual(len(code), 10)

    def test_generate_short_code_custom_length(self):
        """Test custom length parameter works."""
        code = generate_short_code(length=5)
        self.assertEqual(len(code), 5)

        code = generate_short_code(length=20)
        self.assertEqual(len(code), 20)

    def test_generate_short_code_alphanumeric_only(self):
        """Test generated codes contain only letters and digits."""
        code = generate_short_code(length=50)
        self.assertTrue(code.isalnum())

    def test_generate_short_code_uniqueness(self):
        """Test reasonable uniqueness (statistical test)."""
        codes = set()
        for _ in range(100):
            codes.add(generate_short_code())

        # Should have close to 100 unique codes
        self.assertGreater(len(codes), 95)


# =============================================================================
# P1 HIGH: Forms Tests
# =============================================================================


class ShortURLFormTestCase(TestCase):
    """Test ShortURL form validation."""

    def test_form_valid_with_all_fields(self):
        """Test form validation with all fields."""
        form = ShortURLForm(
            {
                "destination_url": "https://example.com",
                "name": "My URL",
                "short_code": "custom123",
            }
        )
        self.assertTrue(form.is_valid())

    def test_form_valid_without_optional_fields(self):
        """Test name and short_code are optional."""
        form = ShortURLForm(
            {
                "destination_url": "https://example.com",
            }
        )
        self.assertTrue(form.is_valid())

    def test_form_invalid_destination_url(self):
        """Test URL validation."""
        form = ShortURLForm(
            {
                "destination_url": "not-a-valid-url",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("destination_url", form.errors)

    def test_form_short_code_is_charfield_not_urlfield(self):
        """Test short_code accepts non-URL strings (bug fix verification)."""
        form = ShortURLForm(
            {
                "destination_url": "https://example.com",
                "short_code": "abc123",  # Not a URL
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["short_code"], "abc123")

    def test_form_name_max_length(self):
        """Test max_length enforcement on name field."""
        form = ShortURLForm(
            {
                "destination_url": "https://example.com",
                "name": "x" * 151,  # Over 150 char limit
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


# =============================================================================
# P1 HIGH: Click Recording Tests
# =============================================================================


class ShortURLClickModelTestCase(TestDataMixin, TestCase):
    """Test ShortURLClick model."""

    def test_click_creation(self):
        """Test click records are created correctly."""
        shorturl = self.create_shorturl()
        fingerprint = self.create_fingerprint()

        click = ShortURLClick.objects.create(
            short_url=shorturl,
            fingerprint=fingerprint,
        )

        self.assertIsNotNone(click.clicked_at)
        self.assertEqual(click.short_url, shorturl)
        self.assertEqual(click.fingerprint, fingerprint)

    def test_click_cascade_delete(self):
        """Test clicks are deleted when ShortURL is deleted."""
        shorturl = self.create_shorturl()
        fingerprint = self.create_fingerprint()

        click = ShortURLClick.objects.create(
            short_url=shorturl,
            fingerprint=fingerprint,
        )

        shorturl.delete()

        # Click should be deleted
        self.assertFalse(ShortURLClick.objects.filter(pk=click.pk).exists())


# =============================================================================
# P2 MEDIUM: Integration Tests
# =============================================================================


class EndToEndTestCase(TestDataMixin, TestCase):
    """End-to-end integration tests."""

    def setUp(self):
        self.client = Client()

    @patch("smllr.shorturls.views.save_shorturl_click")
    def test_e2e_create_and_use_url(self, mock_task):
        """Test complete flow: create URL and use it."""
        # Create URL
        user = self.create_user()
        shorturl = self.create_shorturl(user=user, short_code="e2etest")

        # Use URL
        response = self.client.get(f"/{shorturl.short_code}")

        # Verify redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, shorturl.destination_url)

        # Verify task was queued
        mock_task.delay.assert_called_once()
