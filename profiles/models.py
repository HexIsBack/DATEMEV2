from django.db import models
from django.conf import settings
import base64, json

GENDER_CHOICES   = [('M','Male'),('F','Female'),('NB','Non-binary'),('O','Other')]
INTEREST_CHOICES = [('M','Men'),('F','Women'),('A','Everyone')]
RELATIONSHIP_CHOICES = [
    ('casual',    'Casual / Dating'),
    ('serious',   'Serious Relationship'),
    ('friends',   'Friends First'),
    ('undecided', 'Not Sure Yet'),
]
WANTS_KIDS_CHOICES = [
    ('yes',  'Want kids'),
    ('no',   "Don't want kids"),
    ('open', 'Open to it'),
    ('has',  'Already have kids'),
]
INTEREST_TAGS = [
    'Coffee','Foodie','Traveler','Gamer','Bookworm','Fitness',
    'Music','Movies','Dogs','Cats','Outdoors','Photography',
    'Art','Cooking','Dancing','Sports','Netflix','Hiking',
]
PROMPT_QUESTIONS = [
    'My love language is...',
    "I'm looking for someone who...",
    'The way to my heart is...',
    'My ideal weekend looks like...',
    'A fun fact about me is...',
    'I get excited about...',
    'My guilty pleasure is...',
    'I want to travel to...',
    'My friends describe me as...',
    'Two truths and a lie...',
]


class Profile(models.Model):
    user             = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birth_date       = models.DateField(null=True, blank=True)
    gender           = models.CharField(max_length=2, choices=GENDER_CHOICES, blank=True)
    interested_in    = models.CharField(max_length=2, choices=INTEREST_CHOICES, default='A')
    bio              = models.TextField(max_length=500, blank=True)
    location         = models.CharField(max_length=100, blank=True)
    is_complete      = models.BooleanField(default=False)

    # Location coords (set by browser geolocation)
    latitude         = models.FloatField(null=True, blank=True)
    longitude        = models.FloatField(null=True, blank=True)

    # Deal-breaker preferences
    min_age_pref      = models.IntegerField(default=18)
    max_age_pref      = models.IntegerField(default=60)
    max_distance_km   = models.IntegerField(default=50)
    wants_kids        = models.CharField(max_length=10, choices=WANTS_KIDS_CHOICES, blank=True)
    relationship_type = models.CharField(max_length=15, choices=RELATIONSHIP_CHOICES, blank=True)

    # Interest tags stored as JSON list
    interest_tags     = models.JSONField(default=list, blank=True)

    def age(self):
        if not self.birth_date:
            return None
        from datetime import date
        today = date.today()
        bd = self.birth_date
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))

    def get_photo_url(self):
        """Returns first/main photo URL (backward compat with swipe card)."""
        try:
            photo = ProfilePhoto.objects.using('media_db').filter(user_id=self.user_id).order_by('order').first()
            if photo:
                b64 = base64.b64encode(bytes(photo.data)).decode()
                return f'data:{photo.content_type};base64,{b64}'
            # Fallback to old single image
            img = ProfileImage.objects.using('media_db').get(user_id=self.user_id)
            b64 = base64.b64encode(bytes(img.data)).decode()
            return f'data:{img.content_type};base64,{b64}'
        except Exception:
            return None

    def get_all_photos(self):
        """Returns list of base64 data URLs for photo carousel."""
        photos = []
        for p in ProfilePhoto.objects.using('media_db').filter(user_id=self.user_id).order_by('order'):
            b64 = base64.b64encode(bytes(p.data)).decode()
            photos.append({'id': p.id, 'url': f'data:{p.content_type};base64,{b64}'})
        if not photos:
            url = self.get_photo_url()
            if url:
                photos.append({'id': 0, 'url': url})
        return photos

    def get_prompts(self):
        return UserPrompt.objects.filter(user_id=self.user_id).select_related('prompt')

    def __str__(self):
        return f'{self.user.username} profile'


class ProfileImage(models.Model):
    """Legacy single-photo model — kept for backward compatibility."""
    user_id      = models.IntegerField(unique=True)
    data         = models.BinaryField()
    content_type = models.CharField(max_length=50, default='image/jpeg')
    uploaded_at  = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'profiles'

    def __str__(self):
        return f'Image for user {self.user_id}'


class ProfilePhoto(models.Model):
    """Multiple photos per user — stored in media_db."""
    user_id      = models.IntegerField()
    data         = models.BinaryField()
    content_type = models.CharField(max_length=50, default='image/jpeg')
    order        = models.IntegerField(default=0)
    uploaded_at  = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'profiles'
        ordering  = ['order', 'uploaded_at']

    def __str__(self):
        return f'Photo {self.order} for user {self.user_id}'


class Prompt(models.Model):
    question = models.CharField(max_length=200, unique=True)
    order    = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question


class UserPrompt(models.Model):
    user_id = models.IntegerField()
    prompt  = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    answer  = models.CharField(max_length=300)

    class Meta:
        unique_together = ('user_id', 'prompt')

    def __str__(self):
        return f'User {self.user_id}: {self.prompt.question}'
