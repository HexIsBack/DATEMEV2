from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    photo      = forms.ImageField(required=False, label='Profile Photo')

    class Meta:
        model  = Profile
        fields = ['birth_date', 'gender', 'interested_in', 'bio', 'location']
        widgets = {
            'bio':      forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell others about yourself...'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. Manila, Philippines'}),
        }
