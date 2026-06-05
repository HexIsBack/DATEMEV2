from django.urls import path
from . import views

urlpatterns = [
    path('<int:user_id>/',                  views.chat_view,       name='chat'),
    path('<int:user_id>/messages/',         views.get_messages,    name='get_messages'),
    path('<int:user_id>/poll/',             views.poll_messages,   name='poll_messages'),
    path('<int:user_id>/mark-read/',        views.mark_read,       name='mark_read'),
    path('<int:user_id>/typing-ping/',      views.typing_ping,     name='typing_ping'),
    path('<int:user_id>/typing-status/',    views.typing_status,   name='typing_status'),
    path('react/<int:message_id>/',         views.react_message,   name='react_message'),
    path('notifications/',                  views.notification_poll, name='notification_poll'),
]
