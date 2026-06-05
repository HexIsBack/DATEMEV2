from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from datetime import date

# Common disposable/fake email domains to block
BLOCKED_DOMAINS = {
    'mailinator.com', 'tempmail.com', 'throwaway.email', 'guerrillamail.com',
    'trashmail.com', 'yopmail.com', 'sharklasers.com', 'guerrillamailblock.com',
    'grr.la', 'spam4.me', 'fakeinbox.com', 'maildrop.cc', 'dispostable.com',
    'temp-mail.org', 'getnada.com', 'mailnull.com', '10minutemail.com',
}

class RegistrationForm(UserCreationForm):
    email      = forms.EmailField(required=True)
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type':'date'}),
        help_text='You must be 18 or older to register.'
    )
    class Meta:
        model  = CustomUser
        fields = ['username','email','birth_date','password1','password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('That username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        # Must have exactly one @ with something on both sides
        if email.count('@') != 1:
            raise forms.ValidationError('Enter a valid email address.')

        local, domain = email.split('@')

        # Local part (before @) can't be empty
        if not local:
            raise forms.ValidationError('Enter a valid email address.')

        # Domain must have a dot (e.g. gmail.com)
        if '.' not in domain:
            raise forms.ValidationError('Email domain looks invalid (e.g. gmail.com).')

        # Domain can't start or end with a dot or hyphen
        if domain.startswith('.') or domain.endswith('.') or domain.startswith('-'):
            raise forms.ValidationError('Email domain looks invalid.')

        # Block disposable email domains
        if domain in BLOCKED_DOMAINS:
            raise forms.ValidationError('Disposable or temporary email addresses are not allowed.')

        # Check if already registered
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with that email already exists.')

        return email

    def clean_birth_date(self):
        bd = self.cleaned_data.get('birth_date')
        if bd:
            today = date.today()
            age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
            if age < 18:
                raise forms.ValidationError('You must be at least 18 years old to register.')
        return bd

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1', '')
        p2 = self.cleaned_data.get('password2', '')
        username = self.cleaned_data.get('username', '')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        if p1 and username and p1.lower() == username.lower():
            raise forms.ValidationError('Password cannot be the same as your username.')
        if p1 and len(p1) < 8:
            raise forms.ValidationError('Password must be at least 8 characters.')
        if p1 and p1.isdigit():
            raise forms.ValidationError('Password cannot be entirely numbers.')
        return p2
