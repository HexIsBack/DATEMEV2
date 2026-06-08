from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core import signing
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .forms import RegistrationForm
from .captcha import generate_captcha
from .models import CustomUser


# ── Email verification helpers ────────────────────────────────────────────────

def _send_verification_email(request, user):
    token = signing.dumps(user.pk, salt='email-verification')
    link  = request.build_absolute_uri(f'/accounts/verify-email/{token}/')
    send_mail(
        subject='Verify your DateMe account',
        message=(
            f'Hi {user.username},\n\n'
            f'Click the link below to verify your email address:\n{link}\n\n'
            f'This link expires in 24 hours.\n\n'
            f"If you didn't create a DateMe account, ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


# ── Register ──────────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('swipe')

    captcha_text = request.session.get('captcha_text', '')
    captcha_img  = request.session.get('captcha_img', '')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        user_captcha = request.POST.get('captcha_answer', '').strip().upper()
        if user_captcha != captcha_text:
            messages.error(request, 'CAPTCHA incorrect. Please try again.')
            ct, ci = generate_captcha()
            request.session['captcha_text'] = ct
            request.session['captcha_img']  = ci
            return render(request, 'accounts/register.html', {'form': form, 'captcha_img': ci})

        if form.is_valid():
            user = form.save(commit=False)
            user.email_verified = False
            user.save()
            request.session.pop('captcha_text', None)
            request.session.pop('captcha_img', None)

            # Try to send verification email
            try:
                _send_verification_email(request, user)
                return redirect('verify_email_sent')
            except Exception:
                # Email not configured — activate immediately so they can still use the app
                user.email_verified = True
                user.save()
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


# ── Email verification views ──────────────────────────────────────────────────

def verify_email_sent(request):
    return render(request, 'accounts/verify_email_sent.html')


def verify_email(request, token):
    try:
        user_pk = signing.loads(token, salt='email-verification', max_age=86400)
        user    = CustomUser.objects.get(pk=user_pk)
        user.email_verified = True
        user.save()
        login(request, user)
        messages.success(request, f'Email verified! Welcome to DateMe, {user.username}!')
        return redirect('profile_setup')
    except signing.SignatureExpired:
        messages.error(request, 'That verification link has expired. Request a new one below.')
        return redirect('verify_email_sent')
    except (signing.BadSignature, CustomUser.DoesNotExist):
        messages.error(request, 'Invalid verification link.')
        return redirect('register')


def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = CustomUser.objects.get(email=email, email_verified=False)
            _send_verification_email(request, user)
            messages.success(request, 'Verification email resent! Check your inbox.')
        except CustomUser.DoesNotExist:
            messages.info(request, 'If that email exists and is unverified, we sent a new link.')
        except Exception:
            messages.error(request, 'Could not send email. Check your email settings in settings.py.')
    return redirect('verify_email_sent')


# ── Login / Logout ────────────────────────────────────────────────────────────

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
            if not user.email_verified:
                messages.warning(request, 'Please verify your email before logging in. Check your inbox.')
                return redirect('verify_email_sent')
            login(request, user)
            return redirect('swipe')
        messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ── CAPTCHA & AJAX checks ─────────────────────────────────────────────────────

def refresh_captcha(request):
    ct, ci = generate_captcha()
    request.session['captcha_text'] = ct
    request.session['captcha_img']  = ci
    return JsonResponse({'captcha_img': ci})


def check_username(request):
    username = request.GET.get('username', '').strip()
    taken = CustomUser.objects.filter(username__iexact=username).exists()
    return JsonResponse({'taken': taken})


def check_email(request):
    email = request.GET.get('email', '').strip()
    taken = CustomUser.objects.filter(email__iexact=email).exists()
    return JsonResponse({'taken': taken})
