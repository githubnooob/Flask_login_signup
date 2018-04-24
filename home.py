from flask import Flask,render_template,request,g,request,redirect,url_for,session
from flask_login import LoginManager, UserMixin,login_user, login_required,logout_user, current_user
from flask_sqlalchemy import SQLAlchemy 
import forms
from wtforms.validators import ValidationError
import datetime 
from flask_bcrypt import generate_password_hash as bPass

app = Flask(__name__)
app.secret_key="kjasdh,mvnkasjdioarulzxcmzxcas;ldka;sd"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////root/Desktop/Social_Network/users.db'
app.config['SQLALCHEMY_BINDS'] = {'posts': 'sqlite:////root/Desktop/Social_Network/posts.db'}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

db = SQLAlchemy(app)

db.create_all()


dict_ = {}
def get_all_users():
	users_ = User.query.all()
	global dict_
	for user in users_:
		dict_[user.email] = user.password
		print dict_[user.email]



@app.route("/")
def home():
	return render_template("home.html")

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
			dict_[email] = password_hash
			db.session.add(new_user)
			db.session.commit()
			login_user(new_user)
		except:
			return "ERROR"
		finally:
			db.session.close()
		return redirect(url_for('dashboard'))
	return render_template("register.html",form=form)	

@app.route("/login",methods=['GET','POST'])
def login():
	x = current_user.is_authenticated
	if not x:
		form = forms.LoginForm(request.form)
		if request.method == 'POST' and form.validate():
			user = User.query.filter_by(username=form.username.data).first()
			login_user(user)
			return redirect(url_for("dashboard"))
		else:
			return render_template("login.html",form=form)		
	else:
		return redirect(url_for("dashboard"))	

@login_required
@app.route("/dashboard")
@login_required
def dashboard():
	return "Hello from the other side %s" % current_user.username

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for("home"))				

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html",error = e)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    joined_at = db.Column(db.DateTime(),default =datetime.datetime.now)
    is_hero = db.Column(db.Boolean(),default=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), unique=True, nullable=False)
    score = db.Column(db.Integer, unique=True, nullable=False)
    downVotes = db.Column(db.Integer, nullable=False)
    posted_time = db.Column(db.DateTime(),default =datetime.datetime.now)
    upVotes = db.Column(db.Integer,default=False)


if __name__=="__main__":
	get_all_users()
	app.run(debug=True)
