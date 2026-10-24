"""
Applications views — Mark Applied, List, Detail, Update Status, Delete.
"""
from datetime import datetime, timezone

from bson import ObjectId
from django.shortcuts import render, redirect
from django.contrib import messages

from config.db import get_db
from config.auth import login_required_custom


@login_required_custom
def application_list_view(request):
    """List all user applications."""
    db = get_db()
    uid = request.session['user_id']

    status_filter = request.GET.get('status', '').strip()
    query = {'user_id': uid}
    if status_filter:
        query['status'] = status_filter

    apps_cursor = db.applications.find(query).sort('applied_date', -1)
    apps = []
    for app in apps_cursor:
        # Get job info
        try:
            job = db.jobs.find_one({'_id': ObjectId(app['job_id'])})
        except Exception:
            job = None

        app['_id'] = str(app['_id'])
        app['id'] = app['_id']
        app['job_title'] = job.get('title', 'Unknown') if job else 'Unknown'
        app['job_location'] = job.get('location', '') if job else ''

        if job and job.get('company_id'):
            comp = db.companies.find_one({'_id': ObjectId(job['company_id'])})
            app['company_name'] = comp['name'] if comp else job.get('company', 'Unknown')
        else:
            app['company_name'] = job.get('company', 'Unknown') if job else 'Unknown'

        if 'applied_date' in app and hasattr(app['applied_date'], 'strftime'):
            app['applied_date_display'] = app['applied_date'].strftime('%d %b %Y')
        else:
            app['applied_date_display'] = str(app.get('applied_date', ''))

        apps.append(app)

    # Stats
    total = len(apps)
    counts = {'applied': 0, 'interview': 0, 'selected': 0, 'rejected': 0, 'withdrawn': 0}
    for a in apps:
        s = a.get('status', 'applied')
        if s in counts:
            counts[s] += 1

    return render(request, 'applications/list.html', {
        'applications': apps,
        'status_filter': status_filter,
        'total': total,
        'counts': counts,
    })


@login_required_custom
def mark_applied_view(request, job_id):
    """Mark a job as applied."""
    if request.method == 'POST':
        db = get_db()
        uid = request.session['user_id']

        # Check if already applied
        existing = db.applications.find_one({'user_id': uid, 'job_id': job_id})
        if existing:
            messages.info(request, 'You have already marked this job as applied.')
            return redirect(f'/jobs/{job_id}/')

        # Get job and company info
        try:
            job = db.jobs.find_one({'_id': ObjectId(job_id)})
        except Exception:
            messages.error(request, 'Job not found.')
            return redirect('/jobs/')

        if not job:
            messages.error(request, 'Job not found.')
            return redirect('/jobs/')

        app_doc = {
            'user_id': uid,
            'job_id': job_id,
            'company_id': job.get('company_id', ''),
            'applied_date': datetime.now(timezone.utc),
            'status': 'applied',
            'notes': request.POST.get('notes', '').strip(),
            'created_at': datetime.now(timezone.utc),
        }
        db.applications.insert_one(app_doc)

        # Create notification
        db.notifications.insert_one({
            'user_id': uid,
            'title': 'Application Recorded',
            'message': f'Your application for {job.get("title", "a position")} has been recorded.',
            'type': 'application',
            'is_read': False,
            'created_at': datetime.now(timezone.utc),
        })

        messages.success(request, 'Application saved successfully.')
        return redirect('/applications/')

    return redirect(f'/jobs/{job_id}/')


@login_required_custom
def application_detail_view(request, app_id):
    """View application details."""
    db = get_db()
    uid = request.session['user_id']

    try:
        app = db.applications.find_one({'_id': ObjectId(app_id), 'user_id': uid})
    except Exception:
        messages.error(request, 'Application not found.')
        return redirect('/applications/')

    if not app:
        messages.error(request, 'Application not found.')
        return redirect('/applications/')

    # Get job and company info
    try:
        job = db.jobs.find_one({'_id': ObjectId(app['job_id'])})
    except Exception:
        job = None

    app['_id'] = str(app['_id'])
    app['id'] = app['_id']
    app['job'] = job
    if job:
        job['_id'] = str(job['_id'])
        job['id'] = job['_id']
        if job.get('company_id'):
            comp = db.companies.find_one({'_id': ObjectId(job['company_id'])})
            app['company_name'] = comp['name'] if comp else 'Unknown'
        else:
            app['company_name'] = job.get('company', 'Unknown')

    # Get related interview
    interview = db.interviews.find_one({'application_id': app_id, 'user_id': uid})
    if interview:
        interview['_id'] = str(interview['_id'])
        interview['id'] = interview['_id']

    if 'applied_date' in app and hasattr(app['applied_date'], 'strftime'):
        app['applied_date_display'] = app['applied_date'].strftime('%d %b %Y')

    return render(request, 'applications/detail.html', {
        'application': app,
        'interview': interview,
    })


@login_required_custom
def application_update_view(request, app_id):
    """Update application status and notes."""
    if request.method == 'POST':
        db = get_db()
        uid = request.session['user_id']

        new_status = request.POST.get('status', '').strip()
        notes = request.POST.get('notes', '').strip()

        valid_statuses = ['applied', 'interview', 'selected', 'rejected', 'withdrawn']
        if new_status not in valid_statuses:
            messages.error(request, 'Invalid status.')
            return redirect(f'/applications/{app_id}/')

        update = {'status': new_status}
        if notes:
            update['notes'] = notes

        result = db.applications.update_one(
            {'_id': ObjectId(app_id), 'user_id': uid},
            {'$set': update}
        )

        if result.modified_count:
            # Create notification for status change
            app = db.applications.find_one({'_id': ObjectId(app_id)})
            job_title = 'the position'
            if app and app.get('job_id'):
                try:
                    job = db.jobs.find_one({'_id': ObjectId(app['job_id'])})
                    if job:
                        job_title = job.get('title', 'the position')
                except Exception:
                    pass

            db.notifications.insert_one({
                'user_id': uid,
                'title': 'Application Update',
                'message': f'Your application for {job_title} has been updated to {new_status.title()}.',
                'type': 'application',
                'is_read': False,
                'created_at': datetime.now(timezone.utc),
            })
            messages.success(request, 'Application updated successfully.')
        else:
            messages.error(request, 'Application not found or no changes made.')

        return redirect(f'/applications/{app_id}/')

    return redirect(f'/applications/{app_id}/')


@login_required_custom
def application_delete_view(request, app_id):
    """Delete an application."""
    if request.method == 'POST':
        db = get_db()
        uid = request.session['user_id']
        db.applications.delete_one({'_id': ObjectId(app_id), 'user_id': uid})
        db.interviews.delete_many({'application_id': app_id, 'user_id': uid})
        messages.success(request, 'Application deleted.')
    return redirect('/applications/')
