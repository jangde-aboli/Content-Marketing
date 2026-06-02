# users/decorators.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if hasattr(request.user, 'role') and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return redirect('no_permission')  # You can change this to any page you want
        return wrapper
    return decorator
