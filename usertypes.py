


# Супер класс от которого наследуются классы Visitor, Moderator и Administrator
class User:
	def __init__(self, chat_id, username, status):
		self._chat_id = chat_id
		self._username = username
		self._status = status
		self._nickname = None
		self._is_blocked = False


	@property
	def chat_id(self):
		return self._chat_id


	@property
	def username(self):
		return self._username


	@property
	def status(self):
		return self._status


	@property
	def nickname(self):
		return self._nickname


	def block(self):
		self._is_blocked = True


	def unblock(self):
		self._is_blocked = False


	def set_nickname(self, nickname):
		self._nickname = nickname


	def is_blocked(self):
		return self._is_blocked


	def is_visitor(self):
		return self._status == 'visitor'


	def is_moderator(self):
		return self._status == 'moder'


	def is_administrator(self):
		return self._status == 'admin'

#  
class Visitor(User):
	def __init__(self, chat_id, username):
		super(Visitor, self).__init__(chat_id, username, status='visitor')

#  
class Moderator(User):
	def __init__(self, chat_id, username):
		super(Moderator, self).__init__(chat_id, username, status='moder')

#  
class Administrator(User):
	def __init__(self, chat_id, username):
		super(Administrator, self).__init__(chat_id, username, status='admin')

	# Перезапись метода, с целью обеспечения невозможности  
	# блокировки администратора
	def is_blocked(self):
		return False