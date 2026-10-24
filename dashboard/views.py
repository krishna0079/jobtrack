"""
Dashboard views — Landing Page, User Dashboard, Saved Jobs.
"""
from datetime import datetime, timezone

from bson import ObjectId
from django.shortcuts import render, redirect
from django.contrib import messages

from config.db import get_db
from config.auth import login_required_custom


def landing_view(request):
    """Public landing page with fluid vector hero."""
    if request.session.get('user_id'):
        return redirect('/dashboard/')

    db = get_db()
    # Get some stats and recent jobs for the landing page
    try:
        total_jobs = db.jobs.count_documents({'status': 'active'})
        total_companies = db.companies.count_documents({})
        total_users = db.users.count_documents({})
        recent_jobs = list(db.jobs.find({'status': 'active'}).sort('created_at', -1).limit(6))
        for job in recent_jobs:
            job['_id'] = str(job['_id'])
            job['id'] = job['_id']
            if job.get('company_id'):
                comp = db.companies.find_one({'_id': ObjectId(job['company_id'])})
                job['company_name'] = comp['name'] if comp else job.get('company', 'Unknown')
            else:
                job['company_name'] = job.get('company', 'Unknown')
    except Exception:
        total_jobs = 0
        total_companies = 0
        total_users = 0
        recent_jobs = []

    return render(request, 'landing.html', {
        'total_jobs': total_jobs,
        'total_companies': total_companies,
        'total_users': total_users,
        'recent_jobs': recent_jobs,
    })


@login_required_custom
def dashboard_view(request):
    """User dashboard with stats and overview."""
    db = get_db()
    uid = request.session['user_id']
    now = datetime.now(timezone.utc)

    # Application stats
    applications = list(db.applications.find({'user_id': uid}))
    total_apps = len(applications)
    stats = {'applied': 0, 'interview': 0, 'selected': 0, 'rejected': 0, 'withdrawn': 0}
    for app in applications:
        s = app.get('status', 'applied')
        if s in stats:
            stats[s] += 1

    # Upcoming interviews
    upcoming_interviews = list(
        db.interviews.find({'user_id': uid, 'date': {'$gte': now}}).sort('date', 1).limit(5)
    )
    for iv in upcoming_interviews:
        iv['_id'] = str(iv['_id'])
        iv['id'] = iv['_id']
        if hasattr(iv.get('date'), 'strftime'):
            iv['date_display'] = iv['date'].strftime('%d %b %Y')

    # Recent applications
    recent_apps = list(db.applications.find({'user_id': uid}).sort('applied_date', -1).limit(5))
    for app in recent_apps:
        app['_id'] = str(app['_id'])
        app['id'] = app['_id']
        if app.get('job_id'):
            try:
                job = db.jobs.find_one({'_id': ObjectId(app['job_id'])})
                app['job_title'] = job.get('title', 'Unknown') if job else 'Unknown'
                if job and job.get('company_id'):
                    comp = db.companies.find_one({'_id': ObjectId(job['company_id'])})
                    app['company_name'] = comp['name'] if comp else job.get('company', 'Unknown')
                else:
                    app['company_name'] = job.get('company', 'Unknown') if job else 'Unknown'
            except Exception:
                app['job_title'] = 'Unknown'
                app['company_name'] = 'Unknown'

        if 'applied_date' in app and hasattr(app['applied_date'], 'strftime'):
            app['applied_date_display'] = app['applied_date'].strftime('%d %b')

    # Saved jobs count
    saved_count = db.saved_jobs.count_documents({'user_id': uid})
    unread_notifs = db.notifications.count_documents({'user_id': uid, 'is_read': False})

    return render(request, 'dashboard/dashboard.html', {
        'total_applications': total_apps,
        'stats': stats,
        'upcoming_interviews': upcoming_interviews,
        'recent_applications': recent_apps,
        'saved_count': saved_count,
        'unread_notifications': unread_notifs,
    })


@login_required_custom
def saved_jobs_view(request):
    """List user's saved jobs."""
    db = get_db()
    uid = request.session['user_id']

    saved = list(db.saved_jobs.find({'user_id': uid}).sort('saved_at', -1))
    jobs = []
    for s in saved:
        try:
            job = db.jobs.find_one({'_id': ObjectId(s['job_id'])})
        except Exception:
            job = None

        if job:
            job['_id'] = str(job['_id'])
            job['id'] = job['_id']
            if job.get('company_id'):
                comp = db.companies.find_one({'_id': ObjectId(job['company_id'])})
                job['company_name'] = comp['name'] if comp else job.get('company', 'Unknown')
            else:
                job['company_name'] = job.get('company', 'Unknown')
            jobs.append(job)

    return render(request, 'dashboard/saved_jobs.html', {'saved_jobs': jobs})
