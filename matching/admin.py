from django.contrib import admin
from .models import Swipe, Match, Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display  = ('reporter','reported','reason','status','created')
    list_filter   = ('status','reason')
    search_fields = ('reporter__username','reported__username')
    actions       = ['mark_reviewed','mark_actioned','mark_dismissed']

    def mark_reviewed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='reviewed', reviewed_at=timezone.now())
    def mark_actioned(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='actioned', reviewed_at=timezone.now())
    def mark_dismissed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='dismissed', reviewed_at=timezone.now())

admin.site.register(Swipe)
admin.site.register(Match)
