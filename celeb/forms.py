from celeb.utilities import is_hashed

from wtforms import (Form, TextField, TextAreaField, PasswordField, 
        BooleanField, validators)

optional = [validators.Optional()]
required = [validators.Required()]
username_validators = [validators.Length(min=6, max=28)]
email_validators = [validators.Length(min=6, max=35), validators.Email()]
pass_validators = [
                validators.Required(),
                validators.EqualTo('pass_two', message='Passwords don\'t match'),
                validators.Length(min=6, max=35),
                ]


class Registration(Form):
    username = TextField('Username', username_validators)
    email = TextField('Email Address', email_validators)
    pass_one = PasswordField('Password', pass_validators)
    pass_two = PasswordField('Confirm Password', [validators.Required()])


class Login(Form):
    username = TextField('Username', required)
    password = PasswordField('Password', required)


class EditUser(Form):
    email = TextField('Email Address', email_validators)
    old_pass = PasswordField('Current Password', [validators.Required(), is_hashed])
    pass_one = PasswordField('New Password', pass_validators)
    pass_two = PasswordField('Confirm Password', required)


class EditGallery(Form):
    celeb = TextField('Celebrity', required)
    name = TextField('Name', [validators.Length(min=8, max=56)])
    desc = TextAreaField('Description', required)


class CreateGallery(Form):
    url = TextField('URL', required)
    celeb = TextField('Celebrity', required)
    name = TextField('Name', [validators.Length(min=8, max=56)])
    desc = TextAreaField('Description', required)


#class EditGallery(CreateGallery):
#    selects = BooleanField(optional)
