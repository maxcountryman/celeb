from celeb import db

from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    pwhash = db.Column(db.String(120))
    email = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    is_staff = db.Column(db.Boolean, default=False)
    galleries = db.relationship('Gallery', backref='author', lazy='dynamic')
    
    def __init__(self, username, pwhash, email):
        self.username = unicode(username)
        self.pwhash = pwhash
        self.email = unicode(email)
        self.is_active = True
        self.is_staff = False
    
    def __repr__(self):
        return '<User {0!r}>'.format(self.username)


class Gallery(db.Model):
    __tablename__ = 'gallery'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    celeb = db.Column(db.String(80))
    desc = db.Column(db.Text)
    created_on = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pictures = db.relationship('Picture', backref='gallery', lazy='dynamic')
    
    
    def __init__(self, name, celeb, desc, author, created_on=None):
        self.name = unicode(name)
        self.celeb = unicode(celeb)
        self.desc = unicode(desc)
        self.author = author
        if created_on is None:
            created_on = datetime.utcnow()
        self.created_on = created_on
        
    def __repr__(self):
        return '<Gallery {0!r}>'.format(self.name)


class Picture(db.Model):
    __tablename__ = 'picture'
    id = db.Column(db.Integer, primary_key=True)
    full = db.Column(db.String)
    thumb = db.Column(db.String)
    created_on = db.Column(db.DateTime) 
    gallery_id = db.Column(db.Integer, db.ForeignKey('gallery.id'))
    
    def __init__(self, full, thumb, gallery, created_on=None):
        self.full = unicode(full)
        self.thumb = unicode(thumb)
        self.gallery = gallery
        if created_on is None:
            created_on = datetime.utcnow()
        self.created_on = created_on
