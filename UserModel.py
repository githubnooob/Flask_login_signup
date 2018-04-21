from flask_login import UserMixin
from peewee import *
import datetime

db = SqliteDatabase('user.db')

class User(Model,UserMixin):
    username = CharField(unique=True,max_length=20)
    password = CharField(max_length=100)
    email = CharField(unique=True, max_length=40)
    is_hero = BooleanField(default = False)
    joined_at = DateTimeField(default=datetime.datetime.now)
	
    class Meta:
	        database = db
	        order_by = ('-joined_at',)

    @classmethod        
    def create_user(cls,username,email,password,admin=False):
        try:
            cls.create(username=username,
                email=email,
                password=password,
                is_admin=admin)
        except IntegrityError:
		        raise ValueError ("User Exists")		 

       