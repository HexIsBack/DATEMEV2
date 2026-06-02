from django.urls import path
from . import views

urlpatterns = [
    path('swipe/',              views.swipe_view,        name='swipe'),
    path('do-swipe/',           views.do_swipe,          name='do_swipe'),
    path('matches/',            views.matches_chat_view, name='matches'),
    path('matches/<int:user_id>/', views.matches_chat_view, name='matches_chat'),
    path('report/<int:user_id>/', views.report_user,     name='report_user'),
]
