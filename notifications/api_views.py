"""Notifications API Views"""
from bson import ObjectId
from django.http import JsonResponse
from config.db import get_db
from config.auth import login_required_custom


@login_required_custom
def notifications_api(request):
    """GET: list notifications."""
    db = get_db()
    uid = request.session['user_id']
    notifs = list(db.notifications.find({'user_id': uid}).sort('created_at', -1).limit(50))
    for n in notifs:
        n['_id'] = str(n['_id'])
        n['id'] = n['_id']
        if 'created_at' in n:
            n['created_at'] = n['created_at'].isoformat() if hasattr(n['created_at'], 'isoformat') else str(n['created_at'])
    return JsonResponse({'notifications': notifs})


@login_required_custom
def notification_read_api(request, notif_id):
    """PUT: mark as read."""
    if request.method == 'PUT':
        db = get_db()
        uid = request.session['user_id']
        db.notifications.update_one(
            {'_id': ObjectId(notif_id), 'user_id': uid},
            {'$set': {'is_read': True}}
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)
