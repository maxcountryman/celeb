from celeb import app

from flask import session, g, flash, url_for, redirect, render_template
from flaskext.bcrypt import check_password_hash

from wtforms.validators import ValidationError

from functools import wraps

def is_hashed(form, field):
    if not check_password_hash(g.user.pwhash, field.data):
        raise ValidationError('Invalid password')

def auth_user(user):
    g.user = user
    g.username = user.username
    g.pwhash = user.pwhash
    session['logged_in'] = True
    session['username'] = user.username
    flash('You are logged in as {0}'.format(user.username))

def deauth_user():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out')

def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return inner

def is_superuser(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if not session.get('is_staff'):
            return render_template(
                    'index.html', 
                    error='Invalid user permissions'
                    )
        return f(*args, **kwargs)
    return inner

@app.template_filter('formatdate')
def formatdate(value, format='%H:%M / %d-%m-%Y'):
    return value.strftime(format)
