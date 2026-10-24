"""Notifications context processor — injects unread count into all templates."""
from config.db import get_db


def unread_notifications_count(request):
    """Add unread notification count to template context."""
    count = 0
    user_id = request.session.get('user_id')
    if user_id:
        try:
            db = get_db()
            count = db.notifications.count_documents({'user_id': user_id, 'is_read': False})
        except Exception:
            pass
    return {'unread_notifications_count': count}
