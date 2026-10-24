"""
Interviews views — List, Add, Detail, Edit, Delete.
"""
from datetime import datetime, timezone

from bson import ObjectId
from django.shortcuts import render, redirect
from django.contrib import messages

from config.db import get_db
from config.auth import login_required_custom


@login_required_custom
def interview_list_view(request):
    """List all interviews for current user."""
    db = get_db()
    uid = request.session['user_id']

    interviews_cursor = db.interviews.find({'user_id': uid}).sort('date', 1)
    interviews = []
    now = datetime.now(timezone.utc)

    for iv in interviews_cursor:
        iv['_id'] = str(iv['_id'])
        iv['id'] = iv['_id']
        if 'date' in iv and hasattr(iv['date'], 'strftime'):
            iv['date_display'] = iv['date'].strftime('%d %b %Y')
            iv_date = iv['date']
            # Safely handle timezone aware vs naive
            if iv_date.tzinfo is not None and iv_date.tzinfo.utcoffset(iv_date) is not None:
                iv['is_upcoming'] = iv_date > now
            else:
                iv['is_upcoming'] = iv_date > now.replace(tzinfo=None)
        else:
            iv['is_upcoming'] = False
        interviews.append(iv)

    upcoming = [i for i in interviews if i.get('is_upcoming')]
    past = [i for i in interviews if not i.get('is_upcoming')]

    return render(request, 'interviews/list.html', {
        'upcoming': upcoming,
        'past': past,
        'total': len(interviews),
    })


@login_required_custom
def interview_add_view(request, app_id):
    """Add interview details for an application."""
    db = get_db()
    uid = request.session['user_id']

    # Verify application belongs to user
    app = db.applications.find_one({'_id': ObjectId(app_id), 'user_id': uid})
    if not app:
        messages.error(request, 'Application not found.')
        return redirect('/applications/')

    if request.method == 'POST':
        date_str = request.POST.get('date', '')
        time_str = request.POST.get('time', '')
        interview_type = request.POST.get('type', 'online')
        meeting_link = request.POST.get('meeting_link', '').strip()
        location = request.POST.get('location', '').strip()
        notes = request.POST.get('notes', '').strip()

        # Parse date
        try:
            interview_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            messages.error(request, 'Enter a valid date.')
            return redirect(f'/interviews/add/{app_id}/')

        # Get job info
        job = None
        if app.get('job_id'):
            try:
                job = db.jobs.find_one({'_id': ObjectId(app['job_id'])})
            except Exception:
                pass

        company_name = 'Unknown'
        role = 'Unknown'
        if job:
            role = job.get('title', 'Unknown')
            if job.get('company_id'):
                comp = db.companies.find_one({'_id': ObjectId(job['company_id'])})
                company_name = comp['name'] if comp else job.get('company', 'Unknown')
            else:
                company_name = job.get('company', 'Unknown')

        iv_doc = {
            'application_id': app_id,
            'user_id': uid,
            'company': company_name,
            'role': role,
            'date': interview_date,
            'time': time_str,
            'type': interview_type,
            'meeting_link': meeting_link,
            'location': location,
            'notes': notes,
            'created_at': datetime.now(timezone.utc),
        }
        db.interviews.insert_one(iv_doc)

        # Update application status to interview
        db.applications.update_one(
            {'_id': ObjectId(app_id)},
            {'$set': {'status': 'interview'}}
        )

        # Create notification
        db.notifications.insert_one({
            'user_id': uid,
            'title': 'Interview Scheduled',
            'message': f'Interview for {role} at {company_name} scheduled on {interview_date.strftime("%d %b %Y")} at {time_str}.',
            'type': 'interview',
            'is_read': False,
            'created_at': datetime.now(timezone.utc),
        })

        messages.success(request, 'Interview details saved successfully.')
        return redirect('/interviews/')

    # GET — show form
    app['_id'] = str(app['_id'])
    app['id'] = app['_id']
    job = None
    if app.get('job_id'):
        try:
            job = db.jobs.find_one({'_id': ObjectId(app['job_id'])})
            if job:
                job['_id'] = str(job['_id'])
                job['id'] = job['_id']
        except Exception:
            pass

    return render(request, 'interviews/add.html', {'application': app, 'job': job})


@login_required_custom
def interview_detail_view(request, interview_id):
    """View interview details."""
    db = get_db()
    uid = request.session['user_id']

    try:
        iv = db.interviews.find_one({'_id': ObjectId(interview_id), 'user_id': uid})
    except Exception:
        messages.error(request, 'Interview not found.')
        return redirect('/interviews/')

    if not iv:
        messages.error(request, 'Interview not found.')
        return redirect('/interviews/')

    iv['_id'] = str(iv['_id'])
    iv['id'] = iv['_id']
    if 'date' in iv and hasattr(iv['date'], 'strftime'):
        iv['date_display'] = iv['date'].strftime('%d %b %Y')

    return render(request, 'interviews/detail.html', {'interview': iv})


@login_required_custom
def interview_edit_view(request, interview_id):
    """Edit interview details."""
    db = get_db()
    uid = request.session['user_id']

    if request.method == 'POST':
        date_str = request.POST.get('date', '')
        try:
            interview_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            messages.error(request, 'Enter a valid date.')
            return redirect(f'/interviews/{interview_id}/')

        update = {
            'date': interview_date,
            'time': request.POST.get('time', ''),
            'type': request.POST.get('type', 'online'),
            'meeting_link': request.POST.get('meeting_link', '').strip(),
            'location': request.POST.get('location', '').strip(),
            'notes': request.POST.get('notes', '').strip(),
        }

        db.interviews.update_one(
            {'_id': ObjectId(interview_id), 'user_id': uid},
            {'$set': update}
        )
        messages.success(request, 'Interview updated successfully.')
        return redirect(f'/interviews/{interview_id}/')

    return redirect(f'/interviews/{interview_id}/')


@login_required_custom
def interview_delete_view(request, interview_id):
    """Delete an interview."""
    if request.method == 'POST':
        db = get_db()
        uid = request.session['user_id']
        db.interviews.delete_one({'_id': ObjectId(interview_id), 'user_id': uid})
        messages.success(request, 'Interview deleted.')
    return redirect('/interviews/')
