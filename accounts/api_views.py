"""Accounts API Views"""
from bson import ObjectId
from django.http import JsonResponse
from config.db import get_db
from config.auth import login_required_custom


@login_required_custom
def profile_api(request):
    """GET/PUT user profile."""
    db = get_db()
    user_id = request.session['user_id']

    if request.method == 'GET':
        user = db.users.find_one({'_id': ObjectId(user_id)}, {'password': 0})
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
        user['_id'] = str(user['_id'])
        user['id'] = user['_id']
        if 'created_at' in user:
            user['created_at'] = user['created_at'].isoformat()
        return JsonResponse(user)

    elif request.method == 'PUT':
        import json
        data = json.loads(request.body)
        allowed = ['name', 'phone', 'location', 'skills', 'education', 'experience', 'profile_info']
        update = {k: v for k, v in data.items() if k in allowed}
        db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update})
        return JsonResponse({'message': 'Profile updated successfully.'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)
