import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST
import datetime

from .models import Message, MessageReaction, TypingStatus
from accounts.models import CustomUser
from matching.models import Match


def are_matched(user1, user2):
    return Match.objects.filter(
        Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1),
        is_expired=False
    ).exists()


@login_required
def chat_view(request, user_id):
    me    = request.user
    other = get_object_or_404(CustomUser, id=user_id)
    if not are_matched(me, other):
        return redirect('matches')

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.using('chat_db').create(sender=me.id, receiver=other.id, body=body)
            # sending a message extends/removes expiry
            match = Match.objects.filter(
                Q(user1=me, user2=other) | Q(user1=other, user2=me)
            ).first()
            if match and match.expires_at:
                match.extend_expiry()
        return redirect('chat', user_id=user_id)

    msgs = Message.objects.using('chat_db').filter(
        Q(sender=me.id, receiver=other.id) | Q(sender=other.id, receiver=me.id)
    )
    Message.objects.using('chat_db').filter(sender=other.id, receiver=me.id, is_read=False).update(is_read=True)
    return render(request, 'chat/chat.html', {'other': other, 'chat_msgs': msgs, 'me': me})


@login_required
def get_messages(request, user_id):
    me   = request.user
    msgs = Message.objects.using('chat_db').filter(
        Q(sender=me.id, receiver=user_id) | Q(sender=user_id, receiver=me.id)
    )
    # Fetch reactions for these messages
    msg_ids = list(msgs.values_list('id', flat=True))
    reactions_qs = MessageReaction.objects.using('chat_db').filter(message_id__in=msg_ids)
    reactions_map = {}
    for r in reactions_qs:
        reactions_map.setdefault(r.message_id, []).append({'user_id': r.user_id, 'emoji': r.emoji})

    data = []
    for m in msgs:
        data.append({
            'id':        m.id,
            'sender':    m.sender,
            'body':      m.body,
            'time':      m.timestamp.strftime('%H:%M'),
            'is_read':   m.is_read,
            'reactions': reactions_map.get(m.id, []),
        })
    return JsonResponse({'messages': data})


# ── Poll for new messages (lightweight, last-message-id based) ─────────────
@login_required
def poll_messages(request, user_id):
    """Returns messages newer than ?after=<message_id> for real-time polling."""
    me       = request.user
    after_id = int(request.GET.get('after', 0))
    msgs = Message.objects.using('chat_db').filter(
        Q(sender=me.id, receiver=user_id) | Q(sender=user_id, receiver=me.id),
        id__gt=after_id
    ).order_by('id')

    # Mark incoming as read
    Message.objects.using('chat_db').filter(
        sender=user_id, receiver=me.id, is_read=False, id__gt=after_id
    ).update(is_read=True)

    msg_ids = [m.id for m in msgs]
    reactions_map = {}
    if msg_ids:
        for r in MessageReaction.objects.using('chat_db').filter(message_id__in=msg_ids):
            reactions_map.setdefault(r.message_id, []).append({'user_id': r.user_id, 'emoji': r.emoji})

    data = [{
        'id':        m.id,
        'sender':    m.sender,
        'body':      m.body,
        'time':      m.timestamp.strftime('%H:%M'),
        'is_read':   m.is_read,
        'reactions': reactions_map.get(m.id, []),
    } for m in msgs]

    return JsonResponse({'messages': data})


# ── Read-receipt: mark messages as read ───────────────────────────────────
@login_required
def mark_read(request, user_id):
    me = request.user
    Message.objects.using('chat_db').filter(
        sender=user_id, receiver=me.id, is_read=False
    ).update(is_read=True)
    return JsonResponse({'ok': True})


# ── Typing indicator ──────────────────────────────────────────────────────
@login_required
@require_POST
def typing_ping(request, user_id):
    """Called on every keystroke from the client."""
    me = request.user
    TypingStatus.objects.using('chat_db').update_or_create(
        typer_id=me.id,
        receiver_id=user_id,
        defaults={'updated_at': timezone.now()}
    )
    return JsonResponse({'ok': True})


@login_required
def typing_status(request, user_id):
    """Poll: is user_id typing to me?"""
    me      = request.user
    cutoff  = timezone.now() - datetime.timedelta(seconds=4)
    typing  = TypingStatus.objects.using('chat_db').filter(
        typer_id=user_id,
        receiver_id=me.id,
        updated_at__gte=cutoff
    ).exists()
    return JsonResponse({'typing': typing})


# ── Message reactions ─────────────────────────────────────────────────────
@login_required
@require_POST
def react_message(request, message_id):
    me   = request.user
    data = json.loads(request.body)
    emoji = data.get('emoji', '').strip()
    ALLOWED = {'❤️','😂','😮','😢','👍','🔥'}
    if not emoji or emoji not in ALLOWED:
        return JsonResponse({'error': 'invalid emoji'}, status=400)

    existing = MessageReaction.objects.using('chat_db').filter(
        message_id=message_id, user_id=me.id
    ).first()
    if existing:
        if existing.emoji == emoji:
            # toggle off
            existing.delete()
            action = 'removed'
        else:
            existing.emoji = emoji
            existing.save(update_fields=['emoji'])
            action = 'changed'
    else:
        MessageReaction.objects.using('chat_db').create(
            message_id=message_id, user_id=me.id, emoji=emoji
        )
        action = 'added'

    # Return updated reactions for this message
    reactions = list(
        MessageReaction.objects.using('chat_db')
        .filter(message_id=message_id)
        .values('user_id', 'emoji')
    )
    return JsonResponse({'action': action, 'reactions': reactions})


# ── Notification poll: unread counts + new-match alerts ──────────────────
@login_required
def notification_poll(request):
    """Lightweight endpoint polled every ~5 s from the base template."""
    me = request.user
    from matching.models import Match

    # Unread message count across all conversations
    total_unread = Message.objects.using('chat_db').filter(
        receiver=me.id, is_read=False
    ).count()

    # New matches since last poll (stored in session)
    last_check = request.session.get('notif_last_check')
    now_ts = timezone.now().isoformat()
    new_matches = []

    if last_check:
        from django.utils.dateparse import parse_datetime
        last_dt = parse_datetime(last_check)
        if last_dt:
            fresh = Match.objects.filter(
                Q(user1=me) | Q(user2=me),
                created__gt=last_dt,
                is_expired=False
            ).select_related('user1', 'user2')
            for m in fresh:
                other = m.other_user(me)
                new_matches.append({'username': other.username, 'user_id': other.id})

    request.session['notif_last_check'] = now_ts

    return JsonResponse({
        'unread':      total_unread,
        'new_matches': new_matches,
    })
