import time
import jwt 

SECRET_KEY = "randompasswordgeneratorthing123123%^(*&#(*&!@(#&(&#(&##&(!@#&##(" 
DEFAULT_TIME_IN_MINUTES = 10 
DEFAULT_TIME_IN_SECONDS = DEFAULT_TIME_IN_MINUTES*60

def resetPassword(email):

	encode= jwt.encode( {'reset_password': email, 'exp': time.time() + DEFAULT_TIME_IN_SECONDS }, SECRET_KEY, algorithm='HS256').decode('utf-8')
	return encode
def checkResetPass(token):
	email = None 
	try:
		email = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])['reset_password']
	except:
		return 
	return email

