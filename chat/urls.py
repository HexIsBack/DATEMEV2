from django.urls import path
from . import views
urlpatterns = [
    path('<int:user_id>/',          views.chat_view,    name='chat'),
    path('<int:user_id>/messages/', views.get_messages, name='get_messages'),
]
