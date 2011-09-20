from celeb import app, db
from celeb.forms import (Registration, EditUser, Login, CreateGallery, 
        EditGallery)
from celeb.models import User, Gallery, Picture
from celeb.utilities import auth_user, deauth_user, login_required
from celeb.images import ImageFinder, ImageProcessor

from flask import (request, session, url_for, redirect, render_template, 
        abort, flash)

from flaskext.csrf import csrf_exempt
from flaskext.bcrypt import check_password_hash, generate_password_hash

import os
import datetime

# image resize constants
MIN_SIZE = (300, 300)
RESIZE = (300, 300)
THUMB_SIZE = (200, 200)
THUMB_CROP = (0, 0, 160, 160)

@app.before_request
def before_request():
    pass

@app.after_request
def after_request(response):
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('user', id=session.get('username')))
    
    error = None
    form = Login(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.is_active:
            error = 'Invalid username'
        else:    
            if check_password_hash(user.pw_hash, form.password.data):
                auth_user(user)
                next_url = request.args.get('next')
                if next_url:
                    return redirect(url_for(next_url))
                else:
                    return redirect(url_for('index'))
            else:
                error = 'Invalid password'
    return render_template('login.html', form=form, error=error)

@app.route('/logout')
@login_required
def logout():
    deauth_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('logged_in'):
        flash('You\'re already registered')
        return redirect(url_for('user', id=session.get('username')))
    
    error = None
    form = Registration(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            error = 'That username is already in use'
        else:
            user = User(
                username = form.username.data.lower(),
                pwhash = generate_password_hash(form.pass_one.data),
                email = form.email.data,
                )
            db.session.add(user)
            db.session.commit()
            auth_user(user)
            flash('You were successfully registered and are logged in')
            return redirect(url_for('index'))
    return render_template('register.html', form=form, error=error)

@login_required
@app.route('/user', methods=['GET', 'POST'])
def user():
    user = request.args['id']
    user = User.query.filter_by(username=user).first_or_404()
    form = EditUser(request.form, obj=user)
    if request.method == 'POST' and form.validate():
        form.populate_obj(user)
        user.pw_hash = generate_password_hash(form.newpass.data)
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Your account was successfully updated')
    return render_template('user.html', user=user, form=form)

@login_required
@app.route('/user', methods=['GET', 'DELETE'])
def delete_user():
    user = request.args['id']
    user = User.query.filter_by(username=user).first_or_404()
    if request.method == 'DELETE' or request.args.get('action') == 'delete':
        if user.username != session['username'] or not user.is_staff:
            return abort(500)
        user.is_active = False
        db.session.add(user)
        db.session.commit()
        flash('Account successfully deleted')
        return logout()


@csrf_exempt
@login_required
@app.route('/gallery/new', methods=['GET', 'POST'])
def create_gallery():
    
    error = None
    form = CreateGallery(request.form)
    if request.method == 'POST' and form.validate():
        if Gallery.query.filter_by(name=form.name.data).first():
            error = 'Gallery name already in use. Choose a different name.'
        else:
            user = User.query.filter_by(username=session['username']).first()
            # find and process images
            finder = ImageFinder()
            processor = ImageProcessor(
                    #app.config['UPLOAD_PATH'],
                    '/Users/max/Desktop/celeb/celeb/static/uploads/images',
                    MIN_SIZE,
                    RESIZE,
                    THUMB_SIZE,
                    THUMB_CROP
                    )
            images = finder.find_images(form.url.data)
            images = processor.process(images)
            if images:
                # create gallery
                gallery = Gallery(
                    name = form.name.data, 
                    celeb = form.celeb.data,
                    desc = form.desc.data, 
                    author = user, 
                    )
                db.session.add(gallery)
                db.session.commit()
                # retrieve gallery
                gallery = Gallery.query.filter_by(name=form.name.data).first()
                for image in images:
                    image, extension = os.path.splitext(image)
                    picture = Picture(
                        full = image + extension,
                        thumb = image + '-thumb' + extension,
                        gallery = gallery
                        )
                    db.session.add(picture)
                    db.session.commit()
            #return redirect(url_for('edit_gallery', gallery=gallery.name))
                return redirect(url_for('show_gallery', gallery=gallery.name))
            else:
                error = 'There was a problem processing the URL. Please check URL.'
    return render_template('create_gallery.html', form=form, error=error)

@csrf_exempt
@login_required
@app.route('/gallery/<gallery>', methods=['GET', 'POST'])
def show_gallery(gallery):
    
    gallery = Gallery.query.filter_by(name=gallery).first_or_404()
    return render_template('show_gallery.html', gallery=gallery)

def get_year():
    x = datetime.datetime.now().year
    return x

app.jinja_env.globals['get_year'] = get_year

if __name__ == '__main__':
    if app.config.get('EXTERNAL', False):
        app.run(host=app.config.get('EXTERNAL_HOST', '192.168.0.1'))
    else:
        app.run()
