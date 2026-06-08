from django import forms
from .models import Profile, INTEREST_TAGS, PROMPT_QUESTIONS

class ProfileForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    photo      = forms.ImageField(required=False, label='Profile Photo')

    class Meta:
        model  = Profile
        fields = [
            'birth_date', 'gender', 'interested_in', 'bio', 'location',
            'min_age_pref', 'max_age_pref', 'max_distance_km',
            'wants_kids', 'relationship_type',
        ]
        widgets = {
            'bio':              forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell others about yourself...'}),
            'location':         forms.TextInput(attrs={'placeholder': 'e.g. Manila, Philippines'}),
            'min_age_pref':     forms.NumberInput(attrs={'min': 18, 'max': 99}),
            'max_age_pref':     forms.NumberInput(attrs={'min': 18, 'max': 99}),
            'max_distance_km':  forms.NumberInput(attrs={'min': 1, 'max': 500}),
        }
        labels = {
            'min_age_pref':     'Min age',
            'max_age_pref':     'Max age',
            'max_distance_km':  'Max distance (km)',
            'wants_kids':       'Kids preference',
            'relationship_type':'Looking for',
        }
