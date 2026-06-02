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
