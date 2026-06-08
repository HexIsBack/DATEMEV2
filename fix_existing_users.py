# Run this ONCE with: python manage.py shell < fix_existing_users.py
# This sets email_verified=True for all existing accounts so they can still log in.

from accounts.models import CustomUser
updated = CustomUser.objects.filter(email_verified=False).update(email_verified=True)
print(f'Fixed {updated} accounts — all set to verified.')
