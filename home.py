from flask import Flask,render_template,request,g,request,redirect,url_for,session, flash 
from flask_login import LoginManager, UserMixin,login_user, login_required,logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import re, time 
import forms
import GetAvatar
from wtforms.validators import ValidationError
import datetime
from flask_bcrypt import generate_password_hash as bPass
from flask_mail import Mail, Message 
import reset_pass
from threading import Thread

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
mail = Mail(app)

app.secret_key="kjasdh,mvnkasjdioarulzxcmzxcas;ldka;sd"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////root/Desktop/Social_Network/users.db'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

db = SQLAlchemy(app)
db.create_all()


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    joined_at = db.Column(db.DateTime(),default =datetime.datetime.now)
    is_hero = db.Column(db.Boolean(),default=False)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50))
    post = db.Column(db.String)
    score = db.Column(db.Integer, nullable=False )
    date = db.Column(db.DateTime(),default =datetime.datetime.now)
    img_link = db.Column(db.String)
    news_link = db.Column(db.String)



user_dict_ = {}
def get_all_users():
	users_ = User.query.all()
	global user_dict_
	for user in users_:
		user_dict_[user.email] = user.password
	return user_dict_


post_dict={}
def get_all_posts(page=1):
	posts_paginate = db.session.query(Post).paginate(page,3,False)
	return posts_paginate


@app.route("/",methods=['GET','POST'])
def home():
	page = request.args.get('page',1,type=int)
	posts_paginate = get_all_posts(page)
	next_url = None
	prev_url= None
	print posts_paginate.next_num
	if posts_paginate.has_next:
		next_url = url_for('home',page= (posts_paginate.next_num))
	if posts_paginate.has_prev:
		prev_url = url_for('home',page= (posts_paginate.prev_num))

	print posts_paginate.items
	if request.method == 'POST':
		if current_user.is_authenticated:
			post = request.form.get('title')
			img_link = request.form.get('img_link')
			link = request.form.get('link')
			if  not re.findall(r'http\D*://',link):
				link = 'https://' + str(link)
			try:
				post = Post(post=post, user = current_user.username, img_link= img_link, score=0,news_link=link)
				print "I am here"
				db.session.add(post)
				db.session.commit()
			except:
				return "Error"
			finally:
				db.session.close()
			return redirect(url_for("home",posts=get_all_posts(page),next_url = next_url,prev_url=prev_url))
		else:
			print "GOTME HERE"
			login_form = forms.LoginForm(request.form)
			return redirect(url_for("login",form=login_form))
	return render_template("home.html",posts=posts_paginate.items,next_url = next_url,prev_url=prev_url)

@app.route("/register",methods=['GET','POST'])
def register():
	form = forms.RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		username = form.username.data
		email= form.email.data
		password= form.password.data
		password_hash = bPass(str(password))
		try:
			new_user = User(username=username,email=email,password=password_hash)
			post_dict[email] = password_hash
			db.session.add(new_user)
			db.session.commit()
			login_user(new_user)
		except:
			return "ERROR"
		finally:
			db.session.close()

		return redirect(url_for('home'))
	return render_template("register.html",form=form)

@app.route("/login",methods=['GET','POST'])
def login():
	x = current_user.is_authenticated
	form = forms.LoginForm(request.form)
	if not x:
		if request.method == 'POST' and form.validate():
			user = User.query.filter_by(username=form.username.data).first()
			login_user(user)
			return redirect("profile/"+str(user.username))
		else:
			return render_template("login.html",form=form)
	else:
		user = User.query.filter_by(id=current_user.get_id()).first()
		username = user.username
		return redirect("profile/"+str(username))


@app.route("/profile/<username>")
@login_required
def profile(username):
	user = User.query.filter_by(username=username).first_or_404()
	email = user.email
	avatar = GetAvatar.GetAvatar(email)
	avatar = avatar.getAvatar()
	posts = Post.query.filter_by(user=user.username).all()
	return render_template('profile.html',username=username,posts=posts,avatar = avatar)

@app.route("/profile/")
def profile_check():
	if current_user.is_authenticated:
		user = User.query.filter_by(id=current_user.get_id()).first()
		username = user.username
		return redirect("profile/"+str(user.username))
	else:
		return redirect(url_for("login"))


@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for("home"))

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject,sender,recipients,user):
	receivers = []
	receivers.append(recipients)
	msg = Message(subject, sender = sender, recipients = receivers)
	token = reset_pass.resetPassword(receivers[0])
	username = user.username
	html = render_template("password_reset_link.html",username=username,token=token)
	msg.html = html
	Thread(target=send_async_email, args=(app, msg)).start()

@app.route("/checkResetPassword",methods=['GET','POST'])
def checkPass():
	form = forms.PasswordAgainForm(request.form)
	url_token = request.args.get("token")
	email = reset_pass.checkResetPass(url_token)
	if request.method == "GET":
		if email:
			return render_template("password_again.html",form=form)
		else:
			return redirect(url_for('login'))
	else:
		new_pass = form.password.data
		user = User.query.filter_by(email=email).first()
		user.password = bPass(new_pass)
		db.session.commit()
		return redirect(url_for("login"))


@app.route("/resetPassword",methods=['GET','POST'])
def resetPass():
	if current_user.is_authenticated:
		return redirect(url_for("home"))
	form = forms.PasswordResetForm(request.form)
	if request.method == "POST" and form.validate:
		print "RESET PASSWORD "
		given_email = form.email.data
		user = User.query.filter_by(email = given_email).first()		
		if user:
			send_email(" Reset Password ", "anyone@gmail.com",given_email,user)
			flash(" Confirmation Link has been sent.")
	return render_template("forgot_pass.html",form=form)

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html",error = e)



if __name__=="__main__":
	get_all_users()
	app.run(debug=True)
