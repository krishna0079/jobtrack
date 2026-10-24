"""Interviews API Views"""
import json
from datetime import datetime, timezone
from bson import ObjectId
from django.http import JsonResponse
from config.db import get_db
from config.auth import login_required_custom


@login_required_custom
def interviews_api(request):
    """GET: list interviews. POST: create interview."""
    db = get_db()
    uid = request.session['user_id']

    if request.method == 'GET':
        ivs = list(db.interviews.find({'user_id': uid}).sort('date', 1))
        for iv in ivs:
            iv['_id'] = str(iv['_id'])
            iv['id'] = iv['_id']
            if 'date' in iv:
                iv['date'] = iv['date'].isoformat() if hasattr(iv['date'], 'isoformat') else str(iv['date'])
            if 'created_at' in iv:
                iv['created_at'] = iv['created_at'].isoformat() if hasattr(iv['created_at'], 'isoformat') else str(iv['created_at'])
        return JsonResponse({'interviews': ivs})

    elif request.method == 'POST':
        data = json.loads(request.body)
        doc = {
            'application_id': data.get('application_id', ''),
            'user_id': uid,
            'company': data.get('company', ''),
            'role': data.get('role', ''),
            'date': datetime.fromisoformat(data['date']) if data.get('date') else datetime.now(timezone.utc),
            'time': data.get('time', ''),
            'type': data.get('type', 'online'),
            'meeting_link': data.get('meeting_link', ''),
            'location': data.get('location', ''),
            'notes': data.get('notes', ''),
            'created_at': datetime.now(timezone.utc),
        }
        result = db.interviews.insert_one(doc)
        return JsonResponse({'message': 'Interview created', 'id': str(result.inserted_id)}, status=201)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required_custom
def interview_detail_api(request, interview_id):
    """GET/PUT/DELETE a single interview."""
    db = get_db()
    uid = request.session['user_id']

    if request.method == 'GET':
        iv = db.interviews.find_one({'_id': ObjectId(interview_id), 'user_id': uid})
        if not iv:
            return JsonResponse({'error': 'Not found'}, status=404)
        iv['_id'] = str(iv['_id'])
        iv['id'] = iv['_id']
        if 'date' in iv:
            iv['date'] = iv['date'].isoformat() if hasattr(iv['date'], 'isoformat') else str(iv['date'])
        return JsonResponse(iv)

    elif request.method == 'PUT':
        data = json.loads(request.body)
        allowed = ['date', 'time', 'type', 'meeting_link', 'location', 'notes']
        update = {k: v for k, v in data.items() if k in allowed}
        if 'date' in update:
            update['date'] = datetime.fromisoformat(update['date'])
        db.interviews.update_one({'_id': ObjectId(interview_id), 'user_id': uid}, {'$set': update})
        return JsonResponse({'message': 'Updated'})

    elif request.method == 'DELETE':
        db.interviews.delete_one({'_id': ObjectId(interview_id), 'user_id': uid})
        return JsonResponse({'message': 'Deleted'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)
