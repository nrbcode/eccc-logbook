from functools import wraps
from flask import abort
from flask_login import current_user

# Role based access control
def role_required(*role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.role in role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None

