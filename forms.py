from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError
from wtforms.widgets import TextArea
from home import db
from home import User 
from flask_bcrypt import check_password_hash as cPass


def username_login(form,field):

		user = User.query.filter_by(username=field.data).first()
		if user:
			pass
		else:
			raise ValidationError(" Incorrect Login Username ")

def password_login(form,field):
		user = User.query.filter_by(username=form.username.data).first()
		print user 
		if user:
			print str(user.password) 
			print str(field.data)
			if cPass(user.password,field.data):
				pass
			else:
				raise ValidationError(" Password is not correct. Check Your Password Again! ")
		else:
			raise ValidationError(" Incorrect Password ")			

def verify_username(form, field):
	connection = db.engine.raw_connection()
	cursor = connection.cursor()
	username_check = (cursor.execute('SELECT username FROM user WHERE username = "%s" '%field.data).fetchone())
	if username_check:
		username_check =  str(username_check[0].encode("utf-8"))
		print username_check
		if str(username_check)==field.data:
		    raise ValidationError('Username must be unique')
		

def verify_email(form, field):
	connection = db.engine.raw_connection()
	cursor = connection.cursor()
	email_check = (cursor.execute('SELECT email FROM user WHERE email = "%s" '%field.data).fetchone())
	# email_check = str(cursor.execute('SELECT email FROM user ').fetchall())
	if email_check:
		email_check =  str(email_check[0].encode("utf-8"))
		if str(email_check)==field.data:
		    raise ValidationError('Email is already used. Try Another ')


class RegisterForm(Form):
    username = StringField('Username',[validators.Length(min=4, max=25),verify_username])
    email = StringField('Email',[validators.Length(min=6, max=30),validators.Email(),verify_email])
    password = PasswordField('Password',[validators.Length(min=6, max=50)])


class LoginForm(Form):
	username = StringField('Username',validators=[DataRequired(),username_login])
	password = PasswordField('Password',validators=[DataRequired(),password_login])

class PostForm(Form):
	post = StringField(' Enter Your Question ',widget=TextArea(),validators=[DataRequired(),validators.Length(min=1,max=250)])		

