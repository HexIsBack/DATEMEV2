from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegistrationForm
from .captcha import generate_captcha
from .models import CustomUser

def register_view(request):
    if request.user.is_authenticated:
        return redirect('swipe')

    captcha_text = request.session.get('captcha_text', '')
    captcha_img  = request.session.get('captcha_img', '')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        user_captcha = request.POST.get('captcha_answer','').strip().upper()
        if user_captcha != captcha_text:
            messages.error(request, 'CAPTCHA incorrect. Please try again.')
            ct, ci = generate_captcha()
            request.session['captcha_text'] = ct
            request.session['captcha_img']  = ci
            return render(request, 'accounts/register.html', {'form': form, 'captcha_img': ci})
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            request.session.pop('captcha_text', None)
            request.session.pop('captcha_img', None)
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Please complete your profile.')
            return redirect('profile_setup')
    else:
        form = RegistrationForm()
        ct, ci = generate_captcha()
        request.session['captcha_text'] = ct
        request.session['captcha_img']  = ci
        captcha_img = ci

    return render(request, 'accounts/register.html', {'form': form, 'captcha_img': captcha_img})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('swipe')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_blocked:
                messages.error(request, f'Your account has been blocked. Reason: {user.block_reason or "Policy violation"}')
                return redirect('login')
            login(request, user)
            return redirect('swipe')
        messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def refresh_captcha(request):
    from django.http import JsonResponse
    ct, ci = generate_captcha()
    request.session['captcha_text'] = ct
    request.session['captcha_img']  = ci
    return JsonResponse({'captcha_img': ci})


# ── AJAX availability checks ──────────────────────────────────────────────────

from django.http import JsonResponse

def check_username(request):
    username = request.GET.get('username', '').strip()
    taken = CustomUser.objects.filter(username__iexact=username).exists()
    return JsonResponse({'taken': taken})

def check_email(request):
    email = request.GET.get('email', '').strip()
    taken = CustomUser.objects.filter(email__iexact=email).exists()
    return JsonResponse({'taken': taken})
