from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime

MATCH_EXPIRY_HOURS = 48


class Swipe(models.Model):
    DIRECTION = [('like','Like'),('pass','Pass')]
    swiper    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='swipes_given')
    swiped_on = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='swipes_received')
    direction = models.CharField(max_length=4, choices=DIRECTION)
    created   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('swiper','swiped_on')


class Match(models.Model):
    user1      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='matches_as_user1')
    user2      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='matches_as_user2')
    created    = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user1','user2')

    def other_user(self, user):
        return self.user2 if self.user1 == user else self.user1

    def save(self, *args, **kwargs):
        if not self.pk and not self.expires_at:
            self.expires_at = timezone.now() + datetime.timedelta(hours=MATCH_EXPIRY_HOURS)
        super().save(*args, **kwargs)

    def extend_expiry(self):
        self.expires_at = None
        self.save(update_fields=['expires_at'])

    @property
    def hours_left(self):
        if self.expires_at is None:
            return None
        delta = self.expires_at - timezone.now()
        return max(0, int(delta.total_seconds() / 3600))

    @property
    def is_expiring_soon(self):
        h = self.hours_left
        return h is not None and h <= 6


class Report(models.Model):
    REASONS = [
        ('harassment',   'Harassment'),
        ('fake_profile', 'Fake Profile'),
        ('inappropriate','Inappropriate Content'),
    ]
    STATUS = [
        ('pending',   'Pending'),
        ('reviewed',  'Reviewed'),
        ('dismissed', 'Dismissed'),
        ('actioned',  'Actioned'),
    ]
    reporter    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    reported    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_received')
    reason      = models.CharField(max_length=20, choices=REASONS)
    details     = models.TextField(max_length=500, blank=True)
    status      = models.CharField(max_length=10, choices=STATUS, default='pending')
    created     = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('reporter','reported','reason')

    def __str__(self):
        return f'{self.reporter} reported {self.reported} for {self.reason}'


class Boost(models.Model):
    """30-minute profile boost — boosted users appear first in swipe queue."""
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='boosts')
    activated_at = models.DateTimeField(auto_now_add=True)
    expires_at   = models.DateTimeField()

    @property
    def is_active(self):
        return timezone.now() < self.expires_at

    @property
    def minutes_left(self):
        delta = self.expires_at - timezone.now()
        return max(0, int(delta.total_seconds() / 60))

    def __str__(self):
        return f'{self.user.username} boost ({"active" if self.is_active else "expired"})'
