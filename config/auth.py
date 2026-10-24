"""
Authentication decorators for view protection.
Since we use MongoDB (not Django's auth), we implement custom session-based auth.
"""
from functools import wraps
from django.shortcuts import redirect
from django.http import JsonResponse


def login_required_custom(view_func):
    """Require login via session-based auth with MongoDB."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Authentication required'}, status=401)
            return redirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Require admin role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('/login/')
        if request.session.get('user_role') != 'admin':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Admin access required'}, status=403)
            return redirect('/dashboard/')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_current_user_id(request):
    """Get current user ID from session."""
    return request.session.get('user_id')
