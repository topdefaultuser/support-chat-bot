import contents
import usertypes



class Session:
	"""
	Сессия хранит пользователей, заявки на модерирование и состояние пользовательских и модераторских чатов. 
	При инициализации сессии пользователи загружаются  с базы данных.
	"""
	def __init__(self, db):
		self._db = db
		self._users = {} 
		self._requests = {} # Запросы на получение прав модератора
		self._is_users_chat_work = True 
		self._is_admin_chat_work = True
	
		self._load_users()


	def _load_users(self):
		users_chat_id = self._db.select_users_chat_id()
		# Преобразование [(111111111,), (222222222,)] в [111111111, 222222222] 
		users_chat_id = [chat_id[0] for chat_id in users_chat_id]
		
		for chat_id in users_chat_id:
			user = self._db.load_user_by_chat_id(chat_id)

			self._users[chat_id] = user


	@property
	def is_users_chat_work(self):
		return self._is_users_chat_work


	@property
	def is_admin_chat_work(self):
		return self._is_admin_chat_work


	def enable_users_chat(self):
		self._is_users_chat_work = True


	def disable_users_chat(self):
		self._is_users_chat_work = False


	def enable_admin_chat(self):
		self._is_admin_chat_work = True


	def disable_admin_chat(self):
		self._is_admin_chat_work = False


	def append_user(self, user):
		chat_id = user.chat_id
		self._users[chat_id] = user
		# Записываем данные о пользователя в базу данных 
		self._db.append_user(user)


	def has_user_by_chat_id(self, chat_id: int):
		result = self._users.get(chat_id)
		if(result):
			return True
		else:
			return False


	def is_user_visitor_by_chat_id(self, chat_id: int):
		user = self._users.get(chat_id)
		if(user):
			return user.is_visitor()
		return False


	def is_user_moderator_by_chat_id(self, chat_id: int):
		user = self._users.get(chat_id)
		if(user):
			return user.is_moderator()
		return False


	def is_user_administrator_by_chat_id(self, chat_id: int):
		user = self._users.get(chat_id)
		if(user):
			return user.is_administrator()
		return False


	def is_user_manager_by_chat_id(self, chat_id: int):
		user = self._users.get(chat_id)
		if(user):
			return user.is_administrator() or user.is_moderator()
		return False	


	def is_user_blocked_by_chat_id(self, chat_id: int):
		user = self._users.get(chat_id)
		if(user):
			return user.is_blocked()
		return False


	def get_user_by_chat_id(self, chat_id: int):
		return self._users.get(chat_id)


	def get_user_nickname_by_chat_id(self, chat_id: int):
		user = self._users.get(chat_id)
		if(user):
			return user.nickname


	def get_username_by_chat_id(self, chat_id: int):
		user = self._users.get(chat_id)
		if(user):
			return user.username


	def delete_user_by_chat_id(self, chat_id: int):
		user = self._users.get(chat_id)
		if(user):
			del self._users[chat_id]

			self._db.detele_user_by_chat_id(chat_id)


	def block_user_by_chat_id(self, chat_id: int):
		user = self._users.get(chat_id)
		if(user):
			user.block()
			self._db.update_user_block_status_by_chat_id(chat_id, user.is_blocked())


	def unblock_user_by_chat_id(self, chat_id: int):
		user = self._users.get(chat_id)
		if(user):
			user.unblock()
			self._db.update_user_block_status_by_chat_id(chat_id, user.is_blocked())


	def get_user_status_by_chat_id(self, chat_id: int):
		user = self._users.get(chat_id)
		if(user):
			return user.status
	
		return 'visitor'


	def change_user_status_by_chat_id(self, chat_id: int, status: str):
		pass


	def has_requests_by_chat_id(self, chat_id: int):
		result = self._requests.get(chat_id)
		if(result):
			return True
		return False


	def append_requests(self, chat_id: int, username: str):
		self._requests.update({chat_id: username})


	def delete_requests_by_chat_id(self, chat_id: int):
		del self._requests[chat_id]


	def export_requests(self):
		return self._requests


	def export_managers(self):
		return [user for user in self._users.values() if (user.is_administrator() or user.is_moderator())]


	def export_visitors(self):
		return [user for user in self._users.values() if user.is_visitor()]


	def export_blocked_users(self):
		return [user for user in self._users.values() if user.is_blocked()]

 
class Chat:
	"""
	Если бот был перезапущен, прошлые сообщения не будут загружаться автоматически.
	Сообщения будет подгружено  в случае нажатия на кнопку для ответа на сообщение.
	"""
	def __init__(self, db):
		self._db = db
		self._messages = {}

	# Проверка наличия сообщения в словаре чата или в базе данных
	def has_user_message(self, message_id: str):
		result = self._messages.get(message_id, self._db.has_message(message_id))
		if(result):
			return True
		return False


	def append_message(self, message: contents.Message):
		self._messages[message.id] = message

		self._db.append_message(message)


	def bind_answer(self, from_user_id: int, to_user_id: int, message_id: str):
		self._db.bind_answer(from_user_id, to_user_id, message_id)


	def select_message(self, message_id: str):
		message = self._messages.get(message_id)
		if(not message):
			message = self._db.select_message(message_id)
			# Добавления сообщения с базы данных в словарь сооющений
			self._messages[message_id] = message

		return message


	def update_message(self, message: contents.Message):
		message_id = message.id

		if(self._messages.get(message_id)):
			self._messages.update({message_id: message})

		self._db.update_message(message)


	def delete_message(self, message_id: str):
		if(messages and messages.get(message_id)):
			del self._messages[message_id]

		self._db.delete_message(message_id)

