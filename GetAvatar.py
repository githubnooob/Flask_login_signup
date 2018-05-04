from hashlib import md5

class GetAvatar():
	def __init__(self):
		pass
	def __init__(self,email):
		avatar = 'https://www.gravatar.com/avatar/' + md5(email).hexdigest()
		self.avatar = avatar
	def getAvatar(self):
		return self.avatar