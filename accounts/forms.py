from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from datetime import date

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a real email — this is where your password reset link will be sent.'
    )
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type':'date'}),
        help_text='You must be 18 or older to register.'
    )

    class Meta:
        model  = CustomUser
        fields = ['username', 'email', 'birth_date', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_birth_date(self):
        bd = self.cleaned_data.get('birth_date')
        if bd:
            today = date.today()
            age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
            if age < 18:
                raise forms.ValidationError('You must be at least 18 years old to register.')
        return bd
