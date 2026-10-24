"""Jobs API Views"""
from bson import ObjectId
from django.http import JsonResponse
from config.db import get_db


def jobs_api(request):
    """GET: list active jobs."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    db = get_db()
    jobs_cursor = db.jobs.find({'status': 'active'}).sort('created_at', -1).limit(50)
    jobs = []
    for j in jobs_cursor:
        j['_id'] = str(j['_id'])
        j['id'] = j['_id']
        if 'company_id' in j:
            j['company_id'] = str(j['company_id']) if isinstance(j['company_id'], ObjectId) else j['company_id']
        if 'created_at' in j:
            j['created_at'] = j['created_at'].isoformat() if hasattr(j['created_at'], 'isoformat') else str(j['created_at'])
        if 'deadline' in j:
            j['deadline'] = j['deadline'].isoformat() if hasattr(j['deadline'], 'isoformat') else str(j['deadline'])
        jobs.append(j)
    return JsonResponse({'jobs': jobs})


def job_detail_api(request, job_id):
    """GET: single job detail."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    db = get_db()
    try:
        job = db.jobs.find_one({'_id': ObjectId(job_id)})
    except Exception:
        return JsonResponse({'error': 'Invalid job ID'}, status=400)

    if not job:
        return JsonResponse({'error': 'Job not found'}, status=404)

    job['_id'] = str(job['_id'])
    job['id'] = job['_id']
    if 'created_at' in job:
        job['created_at'] = job['created_at'].isoformat() if hasattr(job['created_at'], 'isoformat') else str(job['created_at'])
    if 'deadline' in job:
        job['deadline'] = job['deadline'].isoformat() if hasattr(job['deadline'], 'isoformat') else str(job['deadline'])
    return JsonResponse(job)
