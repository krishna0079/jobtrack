"""
Accounts views — Registration, Login, Logout, Profile, Google OAuth.
Uses MongoDB via PyMongo for user storage with bcrypt password hashing.
"""
import bcrypt
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from bson import ObjectId
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings

from config.db import get_db
from config.auth import login_required_custom


# ─── Registration ─────────────────────────────────────────────────
def register_view(request):
    if request.session.get('user_id'):
        return redirect('/dashboard/')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')

        # Validation
        errors = []
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        if not email or '@' not in email:
            errors.append('Enter a valid email address.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'accounts/register.html', {'name': name, 'email': email})

        db = get_db()
        if db.users.find_one({'email': email}):
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'accounts/register.html', {'name': name, 'email': email})

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_doc = {
            'name': name,
            'email': email,
            'password': hashed.decode('utf-8'),
            'role': 'job_seeker',
            'phone': '',
            'location': '',
            'skills': [],
            'education': '',
            'experience': '',
            'profile_info': '',
            'resume': '',
            'auth_provider': 'local',
            'created_at': datetime.now(timezone.utc),
        }
        result = db.users.insert_one(user_doc)

        # Auto-login
        request.session['user_id'] = str(result.inserted_id)
        request.session['user_name'] = name
        request.session['user_email'] = email
        request.session['user_role'] = 'job_seeker'
        messages.success(request, 'Registration successful. Welcome to JobTrack!')
        return redirect('/dashboard/')

    return render(request, 'accounts/register.html')


# ─── Login ────────────────────────────────────────────────────────
def login_view(request):
    if request.session.get('user_id'):
        return redirect('/dashboard/')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'accounts/login.html', {'email': email})

        db = get_db()
        user = db.users.find_one({'email': email})

        if not user:
            messages.error(request, 'Invalid email or password.')
            return render(request, 'accounts/login.html', {'email': email})

        stored_pw = user.get('password', '')
        if not stored_pw or not bcrypt.checkpw(password.encode('utf-8'), stored_pw.encode('utf-8')):
            messages.error(request, 'Invalid email or password.')
            return render(request, 'accounts/login.html', {'email': email})

        # Set session
        request.session['user_id'] = str(user['_id'])
        request.session['user_name'] = user['name']
        request.session['user_email'] = user['email']
        request.session['user_role'] = user.get('role', 'job_seeker')
        messages.success(request, f'Welcome back, {user["name"]}!')

        if user.get('role') == 'admin':
            return redirect('/admin-panel/dashboard/')
        return redirect('/dashboard/')

    return render(request, 'accounts/login.html')


# ─── Logout ───────────────────────────────────────────────────────
def logout_view(request):
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('/')


# ─── Profile ──────────────────────────────────────────────────────
@login_required_custom
def profile_view(request):
    db = get_db()
    user = db.users.find_one({'_id': ObjectId(request.session['user_id'])})
    if not user:
        request.session.flush()
        return redirect('/login/')
    user['_id'] = str(user['_id'])
    user['id'] = user['_id']
    return render(request, 'accounts/profile.html', {'user': user})


@login_required_custom
def profile_update_view(request):
    if request.method == 'POST':
        db = get_db()
        user_id = request.session['user_id']

        skills_raw = request.POST.get('skills', '')
        skills = [s.strip() for s in skills_raw.split(',') if s.strip()]

        update_data = {
            'name': request.POST.get('name', '').strip(),
            'phone': request.POST.get('phone', '').strip(),
            'location': request.POST.get('location', '').strip(),
            'skills': skills,
            'education': request.POST.get('education', '').strip(),
            'experience': request.POST.get('experience', '').strip(),
            'profile_info': request.POST.get('profile_info', '').strip(),
        }

        # Handle resume upload
        if request.FILES.get('resume'):
            resume_file = request.FILES['resume']
            if resume_file.size > 5 * 1024 * 1024:  # 5MB limit
                messages.error(request, 'Resume file must be under 5MB.')
                return redirect('/profile/')
            allowed = ['.pdf', '.doc', '.docx']
            ext = '.' + resume_file.name.rsplit('.', 1)[-1].lower() if '.' in resume_file.name else ''
            if ext not in allowed:
                messages.error(request, 'Resume must be PDF, DOC, or DOCX format.')
                return redirect('/profile/')

            import os
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'resumes')
            os.makedirs(upload_dir, exist_ok=True)
            filename = f"{user_id}_{resume_file.name}"
            filepath = os.path.join(upload_dir, filename)
            with open(filepath, 'wb+') as f:
                for chunk in resume_file.chunks():
                    f.write(chunk)
            update_data['resume'] = f'/media/resumes/{filename}'

        db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        request.session['user_name'] = update_data['name']
        messages.success(request, 'Profile updated successfully.')
        return redirect('/profile/')

    return redirect('/profile/')


# ─── Google OAuth ─────────────────────────────────────────────────
def google_login_view(request):
    """Redirect to Google OAuth consent screen."""
    client_id = settings.GOOGLE_CLIENT_ID
    if not client_id:
        messages.error(request, 'Google login is not configured.')
        return redirect('/login/')

    redirect_uri = request.build_absolute_uri('/auth/google/callback/')
    params = urllib.parse.urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent',
    })
    return redirect(f'https://accounts.google.com/o/oauth2/v2/auth?{params}')


def google_callback_view(request):
    """Handle Google OAuth callback."""
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Google authentication failed.')
        return redirect('/login/')

    redirect_uri = request.build_absolute_uri('/auth/google/callback/')
    try:
        # Exchange code for tokens
        token_data = urllib.parse.urlencode({
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }).encode()

        token_req = urllib.request.Request(
            'https://oauth2.googleapis.com/token',
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        with urllib.request.urlopen(token_req, timeout=10) as resp:
            tokens = json.loads(resp.read())

        # Get user info
        user_req = urllib.request.Request(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {tokens["access_token"]}'},
        )
        with urllib.request.urlopen(user_req, timeout=10) as resp:
            google_user = json.loads(resp.read())

        email = google_user.get('email', '').lower()
        name = google_user.get('name', email.split('@')[0])

        db = get_db()
        user = db.users.find_one({'email': email})

        if not user:
            user_doc = {
                'name': name,
                'email': email,
                'password': '',
                'role': 'job_seeker',
                'phone': '',
                'location': '',
                'skills': [],
                'education': '',
                'experience': '',
                'profile_info': '',
                'resume': '',
                'auth_provider': 'google',
                'google_id': google_user.get('id', ''),
                'created_at': datetime.now(timezone.utc),
            }
            result = db.users.insert_one(user_doc)
            user_id = str(result.inserted_id)
        else:
            user_id = str(user['_id'])
            name = user['name']

        request.session['user_id'] = user_id
        request.session['user_name'] = name
        request.session['user_email'] = email
        request.session['user_role'] = user.get('role', 'job_seeker') if user else 'job_seeker'
        messages.success(request, f'Welcome, {name}!')
        return redirect('/dashboard/')

    except Exception:
        messages.error(request, 'Google authentication failed. Please try again.')
        return redirect('/login/')
