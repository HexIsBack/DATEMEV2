from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from .models import Swipe, Match, Report, Boost
from profiles.models import Profile
from accounts.models import CustomUser
import math, datetime


# ── Helpers ───────────────────────────────────────────────────────────────────

def haversine(lat1, lon1, lat2, lon2):
    """Distance in km between two lat/lng points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def expire_stale_matches():
    Match.objects.filter(
        expires_at__lt=timezone.now(),
        is_expired=False,
        expires_at__isnull=False
    ).update(is_expired=True)


# ── Swipe ─────────────────────────────────────────────────────────────────────

@login_required
def swipe_view(request):
    me = request.user
    expire_stale_matches()

    try:
        my_profile = me.profile
        if not my_profile.is_complete:
            return redirect('profile_setup')
    except Profile.DoesNotExist:
        return redirect('profile_setup')

    already_swiped = Swipe.objects.filter(swiper=me).values_list('swiped_on_id', flat=True)

    # Base queryset
    qs = (
        CustomUser.objects
        .exclude(id=me.id)
        .exclude(id__in=already_swiped)
        .exclude(is_blocked=True)
        .exclude(is_staff=True)
        .exclude(is_superuser=True)
        .select_related('profile')
        .filter(profile__is_complete=True)
    )

    # Age range filter
    from datetime import date
    today = date.today()
    try:
        max_birth = date(today.year - my_profile.min_age_pref, today.month, today.day)
        min_birth = date(today.year - my_profile.max_age_pref, today.month, today.day)
        qs = qs.filter(profile__birth_date__range=[min_birth, max_birth])
    except (ValueError, OverflowError):
        pass

    # Evaluate queryset to list for Python-level filtering
    candidates = list(qs)

    # Distance filter (Python-level since SQLite has no spatial support)
    if my_profile.latitude and my_profile.longitude and my_profile.max_distance_km:
        filtered = []
        for u in candidates:
            p = u.profile
            if p.latitude and p.longitude:
                dist = haversine(my_profile.latitude, my_profile.longitude, p.latitude, p.longitude)
                if dist <= my_profile.max_distance_km:
                    u._distance_km = round(dist, 1)
                    filtered.append(u)
            else:
                # No location data — include anyway
                u._distance_km = None
                filtered.append(u)
        candidates = filtered

    # Sort: boosted profiles first
    boosted_ids = set(
        Boost.objects.filter(expires_at__gt=timezone.now()).values_list('user_id', flat=True)
    )
    candidates.sort(key=lambda u: u.id in boosted_ids, reverse=True)

    # Check my own active boost
    my_boost = Boost.objects.filter(user=me, expires_at__gt=timezone.now()).first()

    candidate = candidates[0] if candidates else None

    return render(request, 'matching/swipe.html', {
        'candidate': candidate,
        'my_boost':  my_boost,
    })


@login_required
def do_swipe(request):
    if request.method == 'POST':
        import json
        data      = json.loads(request.body)
        target_id = data.get('target_id')
        direction = data.get('direction')
        me = request.user

        try:
            target = CustomUser.objects.get(id=target_id)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        Swipe.objects.get_or_create(swiper=me, swiped_on=target, defaults={'direction': direction})

        matched = False
        if direction == 'like':
            mutual = Swipe.objects.filter(swiper=target, swiped_on=me, direction='like').exists()
            if mutual:
                if not Match.objects.filter(Q(user1=me, user2=target) | Q(user1=target, user2=me)).exists():
                    Match.objects.create(user1=me, user2=target)
                matched = True

        return JsonResponse({'matched': matched})
    return JsonResponse({'error': 'Invalid'}, status=400)


# ── Boost ─────────────────────────────────────────────────────────────────────

@login_required
def activate_boost(request):
    if request.method == 'POST':
        active = Boost.objects.filter(user=request.user, expires_at__gt=timezone.now()).first()
        if active:
            return JsonResponse({'ok': False, 'minutes_left': active.minutes_left})
        Boost.objects.create(
            user       = request.user,
            expires_at = timezone.now() + datetime.timedelta(minutes=30),
        )
        return JsonResponse({'ok': True, 'minutes': 30})
    return JsonResponse({'error': 'POST only'}, status=400)


# ── Matches & Chat ─────────────────────────────────────────────────────────────

@login_required
def matches_chat_view(request, user_id=None):
    from chat.models import Message
    me = request.user
    expire_stale_matches()

    raw_matches = Match.objects.filter(
        Q(user1=me) | Q(user2=me), is_expired=False
    ).select_related('user1', 'user2')

    match_list = []
    for m in raw_matches:
        other = m.other_user(me)
        if other.is_staff or other.is_superuser:
            continue
        last_msg = Message.objects.using('chat_db').filter(
            Q(sender=me.id, receiver=other.id) | Q(sender=other.id, receiver=me.id)
        ).order_by('-timestamp').first()
        unread = Message.objects.using('chat_db').filter(
            sender=other.id, receiver=me.id, is_read=False
        ).count()
        match_list.append({
            'match':      m,
            'other':      other,
            'last_msg':   last_msg,
            'unread':     unread,
            'hours_left': m.hours_left,
            'expiring':   m.is_expiring_soon,
        })

    match_list.sort(
        key=lambda x: x['last_msg'].timestamp if x['last_msg'] else x['match'].created,
        reverse=True
    )

    active_user  = None
    chat_msgs    = []
    active_match = None

    if user_id:
        active_user  = get_object_or_404(CustomUser, id=user_id)
        active_match = Match.objects.filter(
            Q(user1=me, user2=active_user) | Q(user1=active_user, user2=me),
            is_expired=False
        ).first()

        if active_match:
            if request.method == 'POST':
                body = request.POST.get('body', '').strip()
                if body:
                    Message.objects.using('chat_db').create(
                        sender=me.id, receiver=active_user.id, body=body
                    )
                    if active_match.expires_at:
                        active_match.extend_expiry()
                return redirect('matches_chat', user_id=user_id)

            chat_msgs = Message.objects.using('chat_db').filter(
                Q(sender=me.id, receiver=active_user.id) | Q(sender=active_user.id, receiver=me.id)
            ).order_by('timestamp')

            msg_ids = list(chat_msgs.values_list('id', flat=True))
            from chat.models import MessageReaction
            reactions_map = {}
            for r in MessageReaction.objects.using('chat_db').filter(message_id__in=msg_ids):
                reactions_map.setdefault(r.message_id, []).append({'user_id': r.user_id, 'emoji': r.emoji})

            Message.objects.using('chat_db').filter(
                sender=active_user.id, receiver=me.id, is_read=False
            ).update(is_read=True)

            return render(request, 'matching/matches_chat.html', {
                'match_list':        match_list,
                'active_user':       active_user,
                'active_match':      active_match,
                'chat_msgs':         chat_msgs,
                'reactions_map':     reactions_map,
                'me':                me,
                'reactions_allowed': ['❤️','😂','😮','😢','👍','🔥'],
            })

    return render(request, 'matching/matches_chat.html', {
        'match_list':   match_list,
        'active_user':  active_user,
        'active_match': active_match,
        'chat_msgs':    chat_msgs,
        'me':           me,
    })


# ── Report ─────────────────────────────────────────────────────────────────────

@login_required
def report_user(request, user_id):
    reported = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        reason  = request.POST.get('reason')
        details = request.POST.get('details', '').strip()
        if reason in dict(Report.REASONS):
            Report.objects.get_or_create(
                reporter=request.user, reported=reported, reason=reason,
                defaults={'details': details}
            )
            messages.success(request, 'Report submitted.')
        next_url = request.POST.get('next', 'swipe')
        return redirect(next_url)
    return render(request, 'matching/report.html', {
        'reported': reported,
        'reasons':  Report.REASONS,
        'next':     request.GET.get('next', 'swipe'),
    })
