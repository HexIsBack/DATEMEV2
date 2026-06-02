from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username','email','is_blocked','is_online','last_seen','date_joined')
    list_filter   = ('is_blocked','is_active')
    search_fields = ('username','email')
    actions       = ['block_users','unblock_users']

    fieldsets = UserAdmin.fieldsets + (
        ('Status', {'fields': ('is_blocked','block_reason','last_seen')}),
    )

    def block_users(self, request, queryset):
        queryset.update(is_blocked=True)
    block_users.short_description = 'Block selected users'

    def unblock_users(self, request, queryset):
        queryset.update(is_blocked=False, block_reason='')
    unblock_users.short_description = 'Unblock selected users'
