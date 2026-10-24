"""
Jobs views — Listing, Search, Filter, Detail, Save/Unsave.
"""
from datetime import datetime, timezone

from bson import ObjectId
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

from config.db import get_db
from config.auth import login_required_custom


def job_list_view(request):
    """List all active jobs with optional filtering."""
    db = get_db()
    query = {'status': 'active'}

    # Filters
    location = request.GET.get('location', '').strip()
    job_type = request.GET.get('job_type', '').strip()
    experience = request.GET.get('experience', '').strip()
    category = request.GET.get('category', '').strip()
    company = request.GET.get('company', '').strip()

    if location:
        query['location'] = {'$regex': location, '$options': 'i'}
    if job_type:
        query['job_type'] = job_type
    if experience:
        query['experience'] = experience
    if category:
        query['skills'] = {'$in': [category]}
    if company:
        query['company_id'] = company

    page = int(request.GET.get('page', 1))
    per_page = 12
    skip = (page - 1) * per_page

    total = db.jobs.count_documents(query)
    jobs_cursor = db.jobs.find(query).sort('created_at', -1).skip(skip).limit(per_page)

    jobs = []
    for job in jobs_cursor:
        # Attach company info
        if job.get('company_id'):
            comp = db.companies.find_one({'_id': ObjectId(job['company_id'])})
            job['company_name'] = comp['name'] if comp else 'Unknown'
            job['company_logo'] = comp.get('logo', '') if comp else ''
        else:
            job['company_name'] = job.get('company', 'Unknown')
        job['_id'] = str(job['_id'])
        job['id'] = job['_id']
        if 'created_at' in job and hasattr(job['created_at'], 'strftime'):
            job['created_at_display'] = job['created_at'].strftime('%d %b %Y')
        if 'deadline' in job and hasattr(job['deadline'], 'strftime'):
            job['deadline_display'] = job['deadline'].strftime('%d %b %Y')
        jobs.append(job)

    # Saved job IDs for current user
    saved_ids = set()
    if request.session.get('user_id'):
        saved = db.saved_jobs.find({'user_id': request.session['user_id']})
        saved_ids = {s['job_id'] for s in saved}

    # Get filter options
    locations = db.jobs.distinct('location', {'status': 'active'})
    job_types = db.jobs.distinct('job_type', {'status': 'active'})
    experiences = db.jobs.distinct('experience', {'status': 'active'})
    all_skills = db.jobs.distinct('skills', {'status': 'active'})
    companies_list = list(db.companies.find({}, {'name': 1}).sort('name', 1))
    for c in companies_list:
        c['_id'] = str(c['_id'])
        c['id'] = c['_id']

    total_pages = max(1, (total + per_page - 1) // per_page)

    context = {
        'jobs': jobs,
        'saved_ids': saved_ids,
        'locations': sorted(locations),
        'job_types': sorted(job_types),
        'experiences': experiences,
        'categories': sorted(all_skills),
        'companies': companies_list,
        'current_filters': {
            'location': location,
            'job_type': job_type,
            'experience': experience,
            'category': category,
            'company': company,
        },
        'page': page,
        'total_pages': total_pages,
        'total': total,
    }
    return render(request, 'jobs/list.html', context)


def job_search_view(request):
    """Search jobs by keyword."""
    db = get_db()
    q = request.GET.get('q', '').strip()
    if not q:
        return redirect('/jobs/')

    # Text search
    query = {
        'status': 'active',
        '$or': [
            {'title': {'$regex': q, '$options': 'i'}},
            {'description': {'$regex': q, '$options': 'i'}},
            {'skills': {'$in': [q]}},
            {'location': {'$regex': q, '$options': 'i'}},
        ]
    }

    jobs_cursor = db.jobs.find(query).sort('created_at', -1).limit(50)
    jobs = []
    for job in jobs_cursor:
        if job.get('company_id'):
            comp = db.companies.find_one({'_id': ObjectId(job['company_id'])})
            job['company_name'] = comp['name'] if comp else 'Unknown'
        else:
            job['company_name'] = job.get('company', 'Unknown')
        job['_id'] = str(job['_id'])
        job['id'] = job['_id']
        if 'created_at' in job and hasattr(job['created_at'], 'strftime'):
            job['created_at_display'] = job['created_at'].strftime('%d %b %Y')
        jobs.append(job)

    saved_ids = set()
    if request.session.get('user_id'):
        saved = db.saved_jobs.find({'user_id': request.session['user_id']})
        saved_ids = {s['job_id'] for s in saved}

    return render(request, 'jobs/list.html', {
        'jobs': jobs,
        'saved_ids': saved_ids,
        'search_query': q,
        'total': len(jobs),
        'page': 1,
        'total_pages': 1,
        'locations': [],
        'job_types': [],
        'experiences': [],
        'categories': [],
        'companies': [],
        'current_filters': {},
    })


def job_detail_view(request, job_id):
    """Show complete job details."""
    db = get_db()
    try:
        job = db.jobs.find_one({'_id': ObjectId(job_id)})
    except Exception:
        messages.error(request, 'Job not found.')
        return redirect('/jobs/')

    if not job:
        messages.error(request, 'Job not found.')
        return redirect('/jobs/')

    if job.get('company_id'):
        comp = db.companies.find_one({'_id': ObjectId(job['company_id'])})
        job['company_name'] = comp['name'] if comp else 'Unknown'
        job['company_website'] = comp.get('website', '') if comp else ''
    else:
        job['company_name'] = job.get('company', 'Unknown')

    job['_id'] = str(job['_id'])
    job['id'] = job['_id']
    if 'created_at' in job and hasattr(job['created_at'], 'strftime'):
        job['created_at_display'] = job['created_at'].strftime('%d %b %Y')
    if 'deadline' in job and hasattr(job['deadline'], 'strftime'):
        job['deadline_display'] = job['deadline'].strftime('%d %b %Y')

    # Check if user already applied / saved
    is_applied = False
    is_saved = False
    if request.session.get('user_id'):
        uid = request.session['user_id']
        is_applied = db.applications.find_one({'user_id': uid, 'job_id': job_id}) is not None
        is_saved = db.saved_jobs.find_one({'user_id': uid, 'job_id': job_id}) is not None

    return render(request, 'jobs/detail.html', {
        'job': job,
        'is_applied': is_applied,
        'is_saved': is_saved,
    })


@login_required_custom
def save_job_view(request, job_id):
    """Save a job."""
    if request.method == 'POST':
        db = get_db()
        uid = request.session['user_id']
        existing = db.saved_jobs.find_one({'user_id': uid, 'job_id': job_id})
        if not existing:
            db.saved_jobs.insert_one({
                'user_id': uid,
                'job_id': job_id,
                'saved_at': datetime.now(timezone.utc),
            })
            messages.success(request, 'Job saved successfully.')
        else:
            messages.info(request, 'Job is already saved.')

    return redirect(f'/jobs/{job_id}/')


@login_required_custom
def unsave_job_view(request, job_id):
    """Remove a saved job."""
    if request.method == 'POST':
        db = get_db()
        db.saved_jobs.delete_one({'user_id': request.session['user_id'], 'job_id': job_id})
        messages.success(request, 'Job removed from saved list.')

    referer = request.META.get('HTTP_REFERER', f'/jobs/{job_id}/')
    return redirect(referer)
