from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser
from profiles.models import Profile
from matching.models import Match, Report

@staff_member_required
def admin_dashboard(request):
    users     = CustomUser.objects.filter(is_staff=False).select_related('profile')
    total     = users.count()
    online    = sum(1 for u in users if u.is_online())
    blocked   = users.filter(is_blocked=True).count()
    new_today = users.filter(date_joined__date=timezone.now().date()).count()
    matches   = Match.objects.count()
    reports   = Report.objects.select_related('reporter','reported').order_by('-created')
    pending_reports = reports.filter(status='pending').count()
    context   = {
        'users': users, 'total': total, 'online': online,
        'blocked': blocked, 'new_today': new_today, 'matches': matches,
        'reports': reports, 'pending_reports': pending_reports,
    }
    return render(request, 'accounts/admin_dashboard.html', context)

@staff_member_required
def block_user(request, user_id):
    user   = get_object_or_404(CustomUser, id=user_id)
    reason = request.POST.get('reason','Policy violation')
    user.is_blocked   = True
    user.block_reason = reason
    user.save()
    messages.success(request, f'{user.username} has been blocked.')
    return redirect('custom_admin')

@staff_member_required
def unblock_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_blocked   = False
    user.block_reason = ''
    user.save()
    messages.success(request, f'{user.username} has been unblocked.')
    return redirect('custom_admin')

@staff_member_required
def update_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    status = request.POST.get('status')
    if status in ['reviewed','actioned','dismissed']:
        report.status      = status
        report.reviewed_at = timezone.now()
        report.save()
        if status == 'actioned':
            report.reported.is_blocked   = True
            report.reported.block_reason = f'Reported for {report.get_reason_display()}'
            report.reported.save()
            messages.success(request, f'{report.reported.username} has been blocked based on report.')
        else:
            messages.success(request, f'Report marked as {status}.')
    return redirect('custom_admin')
