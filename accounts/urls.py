from django.urls import path
from . import views, admin_views
urlpatterns = [
    path('',                            views.login_view,           name='login'),
    path('register/',                   views.register_view,        name='register'),
    path('login/',                      views.login_view,           name='login'),
    path('logout/',                     views.logout_view,          name='logout'),
    path('captcha/refresh/',            views.refresh_captcha,      name='refresh_captcha'),
    path('check-username/',             views.check_username,       name='check_username'),
    path('check-email/',                views.check_email,          name='check_email'),
    path('admin-panel/',                admin_views.admin_dashboard,name='custom_admin'),
    path('admin-panel/block/<int:user_id>/',    admin_views.block_user,   name='block_user'),
    path('admin-panel/unblock/<int:user_id>/',  admin_views.unblock_user, name='unblock_user'),
    path('admin-panel/report/<int:report_id>/', admin_views.update_report,name='update_report'),
]
