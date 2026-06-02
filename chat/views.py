from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Message
from accounts.models import CustomUser
from matching.models import Match

def are_matched(user1, user2):
    from django.db.models import Q
    return Match.objects.filter(Q(user1=user1,user2=user2)|Q(user1=user2,user2=user1)).exists()

@login_required
def chat_view(request, user_id):
    me     = request.user
    other  = get_object_or_404(CustomUser, id=user_id)
    if not are_matched(me, other):
        return redirect('matches')

    if request.method == 'POST':
        body = request.POST.get('body','').strip()
        if body:
            Message.objects.using('chat_db').create(sender=me.id, receiver=other.id, body=body)
        return redirect('chat', user_id=user_id)

    msgs = Message.objects.using('chat_db').filter(
        Q(sender=me.id, receiver=other.id) | Q(sender=other.id, receiver=me.id)
    )
    Message.objects.using('chat_db').filter(sender=other.id, receiver=me.id, is_read=False).update(is_read=True)
    return render(request, 'chat/chat.html', {'other': other, 'chat_msgs': msgs, 'me': me})

@login_required
def get_messages(request, user_id):
    me    = request.user
    msgs  = Message.objects.using('chat_db').filter(
        Q(sender=me.id, receiver=user_id) | Q(sender=user_id, receiver=me.id)
    )
    data = [{'sender': m.sender, 'body': m.body, 'time': m.timestamp.strftime('%H:%M')} for m in msgs]
    return JsonResponse({'messages': data})
