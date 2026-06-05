from django.db import models
from django.conf import settings

class Message(models.Model):
    sender    = models.IntegerField()
    receiver  = models.IntegerField()
    body      = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read   = models.BooleanField(default=False)

    class Meta:
        app_label = 'chat'
        ordering  = ['timestamp']


class MessageReaction(models.Model):
    message_id = models.IntegerField()          # FK to Message.id (cross-db safe)
    user_id    = models.IntegerField()
    emoji      = models.CharField(max_length=8)
    created    = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label    = 'chat'
        unique_together = ('message_id', 'user_id')   # one reaction per user per msg


class TypingStatus(models.Model):
    """Ephemeral row: user X is typing to user Y. Updated on every keystroke."""
    typer_id   = models.IntegerField()
    receiver_id = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label    = 'chat'
        unique_together = ('typer_id', 'receiver_id')
