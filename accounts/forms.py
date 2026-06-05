from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser
from datetime import date

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
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email__iexact=email).exists():
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
