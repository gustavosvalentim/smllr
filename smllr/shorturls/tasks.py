import logging

from celery import shared_task
from smllr.shorturls.models import ShortURL, ShortURLClick
from smllr.fingerprint.models import Fingerprint


logger = logging.getLogger(__name__)


@shared_task
def save_shorturl_click(shortcode: str, fingerprint_id: int):
    shorturl = ShortURL.objects.filter(short_code=shortcode).first()

    if not shorturl:
        logger.error(f"ShortURL with code {shortcode} was not found")
        return

    fingerprint = Fingerprint.objects.filter(pk=fingerprint_id).first()

    if not fingerprint:
        logger.error(
            f"Fingerprint for code {shortcode} with ID {fingerprint_id} was not found"
        )
        return

    shorturl.increment_clicks()
    shorturl_click = ShortURLClick.objects.create(
        short_url=shorturl,
        fingerprint=fingerprint,
    )
    shorturl_click.save()
