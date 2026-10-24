"""
Admin Panel views — Dashboard, User/Company/Job management.
"""
import bcrypt
from datetime import datetime, timezone

from bson import ObjectId
from django.shortcuts import render, redirect
from django.contrib import messages

from config.db import get_db
from config.auth import admin_required


def admin_login_view(request):
    """Separate admin login."""
    if request.session.get('user_role') == 'admin':
        return redirect('/admin-panel/dashboard/')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        db = get_db()
        user = db.users.find_one({'email': email, 'role': 'admin'})
        if not user:
            messages.error(request, 'Invalid admin credentials.')
            return render(request, 'adminpanel/login.html')

        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            messages.error(request, 'Invalid admin credentials.')
            return render(request, 'adminpanel/login.html')

        request.session['user_id'] = str(user['_id'])
        request.session['user_name'] = user['name']
        request.session['user_email'] = user['email']
        request.session['user_role'] = 'admin'
        return redirect('/admin-panel/dashboard/')

    return render(request, 'adminpanel/login.html')


@admin_required
def admin_dashboard_view(request):
    """Admin dashboard with statistics."""
    db = get_db()

    context = {
        'total_users': db.users.count_documents({}),
        'total_companies': db.companies.count_documents({}),
        'total_jobs': db.jobs.count_documents({}),
        'total_applications': db.applications.count_documents({}),
        'active_jobs': db.jobs.count_documents({'status': 'active'}),
        'expired_jobs': db.jobs.count_documents({'status': 'expired'}),
    }
    return render(request, 'adminpanel/dashboard.html', context)


@admin_required
def admin_users_view(request):
    """Manage users."""
    db = get_db()
    users_cursor = db.users.find({}, {'password': 0}).sort('created_at', -1)
    users = []
    for u in users_cursor:
        u['_id'] = str(u['_id'])
        u['id'] = u['_id']
        if 'created_at' in u and hasattr(u['created_at'], 'strftime'):
            u['created_at_display'] = u['created_at'].strftime('%d %b %Y')
        users.append(u)

    return render(request, 'adminpanel/users.html', {'users': users})


@admin_required
def admin_companies_view(request):
    """List companies."""
    db = get_db()
    companies = list(db.companies.find().sort('name', 1))
    for c in companies:
        c['_id'] = str(c['_id'])
        c['id'] = c['_id']
        c['job_count'] = db.jobs.count_documents({'company_id': str(c['_id'])})
    return render(request, 'adminpanel/companies.html', {'companies': companies})


@admin_required
def admin_company_add_view(request):
    """Add a company."""
    if request.method == 'POST':
        db = get_db()
        doc = {
            'name': request.POST.get('name', '').strip(),
            'industry': request.POST.get('industry', '').strip(),
            'location': request.POST.get('location', '').strip(),
            'website': request.POST.get('website', '').strip(),
            'description': request.POST.get('description', '').strip(),
            'logo': request.POST.get('logo', '').strip(),
            'created_at': datetime.now(timezone.utc),
        }
        if not doc['name']:
            messages.error(request, 'Company name is required.')
            return render(request, 'adminpanel/company_form.html', {'company': doc, 'action': 'Add'})

        db.companies.insert_one(doc)
        messages.success(request, 'Company added successfully.')
        return redirect('/admin-panel/companies/')

    return render(request, 'adminpanel/company_form.html', {'company': {}, 'action': 'Add'})


@admin_required
def admin_company_edit_view(request, comp_id):
    """Edit a company."""
    db = get_db()

    if request.method == 'POST':
        update = {
            'name': request.POST.get('name', '').strip(),
            'industry': request.POST.get('industry', '').strip(),
            'location': request.POST.get('location', '').strip(),
            'website': request.POST.get('website', '').strip(),
            'description': request.POST.get('description', '').strip(),
            'logo': request.POST.get('logo', '').strip(),
        }
        db.companies.update_one({'_id': ObjectId(comp_id)}, {'$set': update})
        messages.success(request, 'Company updated successfully.')
        return redirect('/admin-panel/companies/')

    company = db.companies.find_one({'_id': ObjectId(comp_id)})
    if not company:
        messages.error(request, 'Company not found.')
        return redirect('/admin-panel/companies/')

    company['_id'] = str(company['_id'])
    company['id'] = company['_id']
    return render(request, 'adminpanel/company_form.html', {'company': company, 'action': 'Edit'})


@admin_required
def admin_company_delete_view(request, comp_id):
    """Delete a company."""
    if request.method == 'POST':
        db = get_db()
        db.companies.delete_one({'_id': ObjectId(comp_id)})
        messages.success(request, 'Company deleted.')
    return redirect('/admin-panel/companies/')


@admin_required
def admin_jobs_view(request):
    """List all jobs."""
    db = get_db()
    jobs = list(db.jobs.find().sort('created_at', -1))
    for j in jobs:
        j['_id'] = str(j['_id'])
        j['id'] = j['_id']
        if j.get('company_id'):
            comp = db.companies.find_one({'_id': ObjectId(j['company_id'])})
            j['company_name'] = comp['name'] if comp else 'Unknown'
        else:
            j['company_name'] = j.get('company', 'Unknown')
        if 'created_at' in j and hasattr(j['created_at'], 'strftime'):
            j['created_at_display'] = j['created_at'].strftime('%d %b %Y')
        j['app_count'] = db.applications.count_documents({'job_id': str(j['_id'])})
    return render(request, 'adminpanel/jobs.html', {'jobs': jobs})


@admin_required
def admin_job_add_view(request):
    """Add a job."""
    db = get_db()

    if request.method == 'POST':
        skills_raw = request.POST.get('skills', '')
        skills = [s.strip() for s in skills_raw.split(',') if s.strip()]

        deadline_str = request.POST.get('deadline', '')
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').replace(tzinfo=timezone.utc) if deadline_str else None
        except ValueError:
            deadline = None

        doc = {
            'title': request.POST.get('title', '').strip(),
            'company_id': request.POST.get('company_id', '').strip(),
            'company': '',
            'location': request.POST.get('location', '').strip(),
            'job_type': request.POST.get('job_type', '').strip(),
            'experience': request.POST.get('experience', '').strip(),
            'salary': request.POST.get('salary', '').strip(),
            'skills': skills,
            'description': request.POST.get('description', '').strip(),
            'requirements': request.POST.get('requirements', '').strip(),
            'application_url': request.POST.get('application_url', '').strip(),
            'deadline': deadline,
            'status': request.POST.get('status', 'active'),
            'created_at': datetime.now(timezone.utc),
        }

        # Set company name from company_id
        if doc['company_id']:
            try:
                comp = db.companies.find_one({'_id': ObjectId(doc['company_id'])})
                doc['company'] = comp['name'] if comp else ''
            except Exception:
                pass

        if not doc['title']:
            messages.error(request, 'Job title is required.')
            companies = list(db.companies.find({}, {'name': 1}).sort('name', 1))
            for c in companies:
                c['_id'] = str(c['_id'])
                c['id'] = c['_id']
            return render(request, 'adminpanel/job_form.html', {'job': doc, 'companies': companies, 'action': 'Add'})

        db.jobs.insert_one(doc)

        # Notify all users about new job
        users = db.users.find({'role': 'job_seeker'}, {'_id': 1})
        notifs = []
        for u in users:
            notifs.append({
                'user_id': str(u['_id']),
                'title': 'New Job Available',
                'message': f'A new {doc["title"]} position has been added.',
                'type': 'new_job',
                'is_read': False,
                'created_at': datetime.now(timezone.utc),
            })
        if notifs:
            db.notifications.insert_many(notifs)

        messages.success(request, 'Job added successfully.')
        return redirect('/admin-panel/jobs/')

    companies = list(db.companies.find({}, {'name': 1}).sort('name', 1))
    for c in companies:
        c['_id'] = str(c['_id'])
        c['id'] = c['_id']
    return render(request, 'adminpanel/job_form.html', {'job': {}, 'companies': companies, 'action': 'Add'})


@admin_required
def admin_job_edit_view(request, job_id):
    """Edit a job."""
    db = get_db()

    if request.method == 'POST':
        skills_raw = request.POST.get('skills', '')
        skills = [s.strip() for s in skills_raw.split(',') if s.strip()]

        deadline_str = request.POST.get('deadline', '')
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').replace(tzinfo=timezone.utc) if deadline_str else None
        except ValueError:
            deadline = None

        update = {
            'title': request.POST.get('title', '').strip(),
            'company_id': request.POST.get('company_id', '').strip(),
            'location': request.POST.get('location', '').strip(),
            'job_type': request.POST.get('job_type', '').strip(),
            'experience': request.POST.get('experience', '').strip(),
            'salary': request.POST.get('salary', '').strip(),
            'skills': skills,
            'description': request.POST.get('description', '').strip(),
            'requirements': request.POST.get('requirements', '').strip(),
            'application_url': request.POST.get('application_url', '').strip(),
            'deadline': deadline,
            'status': request.POST.get('status', 'active'),
        }

        if update.get('company_id'):
            try:
                comp = db.companies.find_one({'_id': ObjectId(update['company_id'])})
                update['company'] = comp['name'] if comp else ''
            except Exception:
                pass

        db.jobs.update_one({'_id': ObjectId(job_id)}, {'$set': update})
        messages.success(request, 'Job updated successfully.')
        return redirect('/admin-panel/jobs/')

    job = db.jobs.find_one({'_id': ObjectId(job_id)})
    if not job:
        messages.error(request, 'Job not found.')
        return redirect('/admin-panel/jobs/')

    job['_id'] = str(job['_id'])
    job['id'] = job['_id']
    if job.get('deadline') and hasattr(job['deadline'], 'strftime'):
        job['deadline_input'] = job['deadline'].strftime('%Y-%m-%d')
    if job.get('skills'):
        job['skills_str'] = ', '.join(job['skills'])

    companies = list(db.companies.find({}, {'name': 1}).sort('name', 1))
    for c in companies:
        c['_id'] = str(c['_id'])
        c['id'] = c['_id']

    return render(request, 'adminpanel/job_form.html', {'job': job, 'companies': companies, 'action': 'Edit'})


@admin_required
def admin_job_delete_view(request, job_id):
    """Delete a job."""
    if request.method == 'POST':
        db = get_db()
        db.jobs.update_one({'_id': ObjectId(job_id)}, {'$set': {'status': 'deleted'}})
        messages.success(request, 'Job deleted.')
    return redirect('/admin-panel/jobs/')


import urllib.request
import urllib.parse
import json

@admin_required
def admin_job_fetch_view(request):
    """Fetch jobs from Remotive API and save them."""
    if request.method == 'POST':
        search_term = request.POST.get('search_term', '').strip()
        limit_val = int(request.POST.get('limit', '10'))
        
        if not search_term:
            messages.error(request, 'Search term is required.')
            return render(request, 'adminpanel/job_fetch_form.html')
            
        try:
            url = f"https://remotive.com/api/remote-jobs?search={urllib.parse.quote(search_term)}&limit={limit_val}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            jobs_to_insert = []
            db = get_db()
            now = datetime.now(timezone.utc)
            
            jobs_list = data.get('jobs', [])[:limit_val]
            
            if not jobs_list:
                messages.warning(request, f'No jobs found for "{search_term}".')
                return render(request, 'adminpanel/job_fetch_form.html')
                
            for j in jobs_list:
                doc = {
                    'title': j.get('title', ''),
                    'company_id': '',
                    'company': j.get('company_name', 'Unknown'),
                    'location': j.get('candidate_required_location', 'Remote'),
                    'job_type': j.get('job_type', '').replace('_', ' ').title() or 'Remote',
                    'experience': 'Not Specified',
                    'salary': j.get('salary', '') or 'Not Specified',
                    'skills': j.get('tags', []),
                    'description': j.get('description', ''),
                    'requirements': 'See description for details.',
                    'application_url': j.get('url', ''),
                    'deadline': None,
                    'status': 'active',
                    'created_at': now,
                }
                jobs_to_insert.append(doc)
                
            if jobs_to_insert:
                db.jobs.insert_many(jobs_to_insert)
                
                # Notify users
                users = db.users.find({'role': 'job_seeker'}, {'_id': 1})
                notifs = []
                for u in users:
                    notifs.append({
                        'user_id': str(u['_id']),
                        'title': 'New Jobs Fetched!',
                        'message': f'{len(jobs_to_insert)} new {search_term} positions have been added via Auto-Fetch.',
                        'type': 'new_job',
                        'is_read': False,
                        'created_at': now,
                    })
                if notifs:
                    db.notifications.insert_many(notifs)
                    
            messages.success(request, f'Successfully fetched and added {len(jobs_list)} jobs!')
            return redirect('/admin-panel/jobs/')
            
        except Exception as e:
            messages.error(request, f'Error fetching jobs: {str(e)}')
            return render(request, 'adminpanel/job_fetch_form.html')
            
    return render(request, 'adminpanel/job_fetch_form.html')
