"""
Management command: expire matches that passed their deadline with no messages.
Run via cron or scheduler:  python manage.py expire_matches
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from matching.models import Match


class Command(BaseCommand):
    help = 'Expire unresponded matches past their expiry deadline.'

    def handle(self, *args, **options):
        qs = Match.objects.filter(
            expires_at__lt=timezone.now(),
            is_expired=False,
            expires_at__isnull=False,
        )
        count = qs.update(is_expired=True)
        self.stdout.write(self.style.SUCCESS(f'Expired {count} match(es).'))
