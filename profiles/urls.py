from django.urls import path
from . import views

urlpatterns = [
    path('setup/',                      views.profile_setup, name='profile_setup'),
    path('me/',                         views.my_profile,    name='my_profile'),
    path('photo/<int:user_id>/',        views.serve_photo,   name='serve_photo'),
    path('photo/delete/<int:photo_id>/',views.delete_photo,  name='delete_photo'),
]
