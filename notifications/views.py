"""
Notifications views — List, Mark Read, Mark All Read.
"""
from bson import ObjectId
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

from config.db import get_db
from config.auth import login_required_custom


@login_required_custom
def notification_list_view(request):
    """List all notifications for current user."""
    db = get_db()
    uid = request.session['user_id']

    notifs_cursor = db.notifications.find({'user_id': uid}).sort('created_at', -1).limit(100)
    notifs = []
    for n in notifs_cursor:
        n['_id'] = str(n['_id'])
        n['id'] = n['_id']
        if 'created_at' in n and hasattr(n['created_at'], 'strftime'):
            n['created_at_display'] = n['created_at'].strftime('%d %b %Y, %I:%M %p')
        notifs.append(n)

    unread_count = sum(1 for n in notifs if not n.get('is_read'))

    return render(request, 'notifications/list.html', {
        'notifications': notifs,
        'unread_count': unread_count,
    })


@login_required_custom
def mark_read_view(request, notif_id):
    """Mark a single notification as read."""
    if request.method == 'POST':
        db = get_db()
        uid = request.session['user_id']
        db.notifications.update_one(
            {'_id': ObjectId(notif_id), 'user_id': uid},
            {'$set': {'is_read': True}}
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
    return redirect('/notifications/')


@login_required_custom
def mark_all_read_view(request):
    """Mark all notifications as read."""
    if request.method == 'POST':
        db = get_db()
        uid = request.session['user_id']
        db.notifications.update_many(
            {'user_id': uid, 'is_read': False},
            {'$set': {'is_read': True}}
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
    return redirect('/notifications/')
