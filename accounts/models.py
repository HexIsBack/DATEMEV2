from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    is_blocked = models.BooleanField(default=False)
    block_reason = models.TextField(blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)

    def is_online(self):
        if not self.last_seen:
            return False
        return (timezone.now() - self.last_seen).seconds < 300

    def __str__(self):
        return self.username
