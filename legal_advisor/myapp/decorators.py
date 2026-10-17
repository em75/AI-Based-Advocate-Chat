from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def login_required_custom(user_type=None):
    """
    Custom decorator to require login and optionally check user type.
    
    Usage:
    @login_required_custom() - Requires login for any user type
    @login_required_custom('User') - Requires login and User type
    @login_required_custom('Advocate') - Requires login and Advocate type
    @login_required_custom('Admin') - Requires login and Admin type
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access this page.')
                return redirect('/login/')
            
            if user_type and request.user.userType != user_type:
                messages.error(request, f'Access denied. {user_type} access required.')
                return redirect('/login/')
                
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def user_login_required(view_func):
    """Decorator specifically for User role"""
    return login_required_custom('User')(view_func)

def advocate_login_required(view_func):
    """Decorator specifically for Advocate role"""
    return login_required_custom('Advocate')(view_func)

def admin_login_required(view_func):
    """Decorator specifically for Admin role"""
    return login_required_custom('Admin')(view_func)
