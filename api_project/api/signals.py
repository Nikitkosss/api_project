import logging

from django.db.models import signals
from django.dispatch import receiver
from django.utils import timezone

from newsletter.models import MailingList
from api.tasks import make_distribution


logger = logging.getLogger('main')


@receiver(signals.post_save, sender=MailingList)
def create_distribution(sender, instance, created, **kwargs):
    now = timezone.now()

    start_after = 1
    if instance.time_start > now:
        start_after = int((instance.time_start - now).total_seconds())

    make_distribution.apply_async([instance.id,], countdown=start_after)
    logger.info(f'DISTRIBUTION:{instance.id} created. Start over {start_after} sec.')
