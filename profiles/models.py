from django.db import models
from django.conf import settings
import base64

GENDER_CHOICES   = [('M','Male'),('F','Female'),('NB','Non-binary'),('O','Other')]
INTEREST_CHOICES = [('M','Men'),('F','Women'),('A','Everyone')]

class Profile(models.Model):
    user          = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birth_date    = models.DateField(null=True, blank=True)
    gender        = models.CharField(max_length=2, choices=GENDER_CHOICES, blank=True)
    interested_in = models.CharField(max_length=2, choices=INTEREST_CHOICES, default='A')
    bio           = models.TextField(max_length=500, blank=True)
    location      = models.CharField(max_length=100, blank=True)
    is_complete   = models.BooleanField(default=False)

    def age(self):
        if not self.birth_date:
            return None
        from datetime import date
        today = date.today()
        bd = self.birth_date
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))

    def get_photo_url(self):
        try:
            img = ProfileImage.objects.using('media_db').get(user_id=self.user_id)
            b64 = base64.b64encode(img.data).decode()
            return f'data:{img.content_type};base64,{b64}'
        except ProfileImage.DoesNotExist:
            return None

    def __str__(self):
        return f'{self.user.username} profile'


class ProfileImage(models.Model):
    user_id      = models.IntegerField(unique=True)
    data         = models.BinaryField()
    content_type = models.CharField(max_length=50, default='image/jpeg')
    uploaded_at  = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'profiles'

    def __str__(self):
        return f'Image for user {self.user_id}'
