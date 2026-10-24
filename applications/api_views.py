"""Applications API Views"""
import json
from datetime import datetime, timezone
from bson import ObjectId
from django.http import JsonResponse
from config.db import get_db
from config.auth import login_required_custom


@login_required_custom
def applications_api(request):
    """GET: list user applications. POST: create application."""
    db = get_db()
    uid = request.session['user_id']

    if request.method == 'GET':
        apps = list(db.applications.find({'user_id': uid}).sort('applied_date', -1))
        for a in apps:
            a['_id'] = str(a['_id'])
            a['id'] = a['_id']
            if 'applied_date' in a:
                a['applied_date'] = a['applied_date'].isoformat() if hasattr(a['applied_date'], 'isoformat') else str(a['applied_date'])
            if 'created_at' in a:
                a['created_at'] = a['created_at'].isoformat() if hasattr(a['created_at'], 'isoformat') else str(a['created_at'])
        return JsonResponse({'applications': apps})

    elif request.method == 'POST':
        data = json.loads(request.body)
        job_id = data.get('job_id')
        if not job_id:
            return JsonResponse({'error': 'job_id is required'}, status=400)

        existing = db.applications.find_one({'user_id': uid, 'job_id': job_id})
        if existing:
            return JsonResponse({'error': 'Already applied'}, status=409)

        doc = {
            'user_id': uid,
            'job_id': job_id,
            'company_id': data.get('company_id', ''),
            'applied_date': datetime.now(timezone.utc),
            'status': 'applied',
            'notes': data.get('notes', ''),
            'created_at': datetime.now(timezone.utc),
        }
        result = db.applications.insert_one(doc)
        return JsonResponse({'message': 'Application created', 'id': str(result.inserted_id)}, status=201)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required_custom
def application_detail_api(request, app_id):
    """GET/PUT/DELETE a single application."""
    db = get_db()
    uid = request.session['user_id']

    if request.method == 'GET':
        app = db.applications.find_one({'_id': ObjectId(app_id), 'user_id': uid})
        if not app:
            return JsonResponse({'error': 'Not found'}, status=404)
        app['_id'] = str(app['_id'])
        app['id'] = app['_id']
        if 'applied_date' in app:
            app['applied_date'] = app['applied_date'].isoformat() if hasattr(app['applied_date'], 'isoformat') else str(app['applied_date'])
        return JsonResponse(app)

    elif request.method == 'PUT':
        data = json.loads(request.body)
        allowed = ['status', 'notes']
        update = {k: v for k, v in data.items() if k in allowed}
        db.applications.update_one({'_id': ObjectId(app_id), 'user_id': uid}, {'$set': update})
        return JsonResponse({'message': 'Updated'})

    elif request.method == 'DELETE':
        db.applications.delete_one({'_id': ObjectId(app_id), 'user_id': uid})
        return JsonResponse({'message': 'Deleted'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)
