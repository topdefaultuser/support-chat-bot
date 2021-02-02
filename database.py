import sqlite3

import contents
import usertypes



class SQLiteDatabase:
	def __init__(self, filename):
		self._filename = filename

	# Возвращет соединение и курсор
	def __connect(self):
		conn = sqlite3.connect(self._filename)
		return conn, conn.cursor()

	# 
	def create_users_table(self):
		connection, cursor = self.__connect() 
		query = """
			CREATE TABLE "users" (
				"chat_id"	INTEGER,
				"username"	TEXT,
				"status"	TEXT,
				"is_blocked"	INTEGER,
				"nickname"	TEXT
			)
			"""
		cursor.execute(query)
		connection.commit()
		connection.close()

	# 
	def create_messages_table(self):
		connection, cursor = self.__connect() 
		query = """
			CREATE TABLE "messages" (
				"id"	TEXT,
				"chat_id"	INTEGER,
				"message_id"	INTEGER,
				"username"	TEXT,
				"message"	TEXT,
				"type"	TEXT,
				"body"	TEXT,
				"file_id"	TEXT,
				"responses"	INTEGER,
				"recipients_chat_and_message_id"	TEXT
			);
			"""
		cursor.execute(query)
		connection.commit()
		connection.close()

	# 
	def create_answers_table(self):
		connection, cursor = self.__connect() 
		query = """
			CREATE TABLE "answers" (
				"from"	INTEGER,
				"to"	INTEGER,
				"message_id"	INTEGER
			);
			"""
		cursor.execute(query)
		connection.commit()
		connection.close()

	# 
	def append_user(self, data: dict):
		connection, cursor = self.__connect() 
		query = '''INSERT INTO users (chat_id, username, status, nickname, is_blocked) VALUES ("%s", "%s", "%s", "%s", "%s")''' % (
			data['chat_id'], data['username'], data['status'], data['nickname'], data['is_blocked'])

		cursor.execute(query)
		connection.commit()
		connection.close()

	# Получение списка чат айди пользователей 
	def select_users_chat_id(self):
		connection, cursor = self.__connect()
		query = '''SELECT (chat_id) FROM users'''
		result = cursor.execute(query).fetchall()
		connection.close()
		return result

	# Получение значений с таблицы по их 
	def load_user_by_chat_id(self, chat_id: int):
		connection, cursor = self.__connect()
		query = '''SELECT * FROM users WHERE chat_id="%s"''' % chat_id
		result = cursor.execute(query).fetchone()
		connection.close()
		return result


	def update_user_nickname_by_chat_id(self, chat_id: int, nickname: str):
		connection, cursor = self.__connect()
		query = '''UPDATE users SET nickname="%s" WHERE chat_id="%s"''' % (nickname, chat_id)
		cursor.execute(query)
		connection.commit()
		connection.close()


	def update_user_block_status_by_chat_id(self, chat_id: int, status: str):
		connection, cursor = self.__connect()
		query = '''UPDATE users SET is_blocked="%s" WHERE chat_id="%s"''' % (status, chat_id)
		cursor.execute(query)
		connection.commit()
		connection.close()

	# Удаленте пользователя по его чат айди
	def detele_user_by_chat_id(self, chat_id: int):
		connection, cursor = self.__connect()
		query = '''DELETE FROM users WHERE chat_id= "%s"''' % chat_id
		cursor.execute(query)
		connection.commit()
		connection.close()

	# 
	def append_message(self, data: dict):
		connection, cursor = self.__connect()
		query = '''INSERT INTO messages VALUES ("%s", "%i", "%i", "%s", "%s", "%s", "%s", "%s", "%i", "%s")''' % (
			data['id'], data['chat_id'], data['message_id'], data['username'], data['message'], data['type'], 
			data['body'], data['file_id'], data['responses'], data['recipients_chat_and_message_id'])

		cursor.execute(query)
		connection.commit()
		connection.close()

	# У сообщения изменяются только количество ответов, а так же chat, message id, тех кто их получил
	def update_message(self, data: dict):
		connection, cursor = self.__connect()
		query = '''UPDATE messages SET body="%s", responses="%i", recipients_chat_and_message_id="%s" WHERE id="%s"''' % (
			data['body'], data['responses'], data['recipients_chat_and_message_id'], data['id'])

		cursor.execute(query)
		connection.commit()
		connection.close()


	def has_message(self, message_id: str):
		connection, cursor = self.__connect()
		query = '''SELECT * FROM messages WHERE id="%s"''' % message_id
		result = cursor.execute(query).fetchone()
		connection.close()
		return result		


	def select_messge(self, message_id: str):
		connection, cursor = self.__connect()
		query = '''SELECT * FROM messages WHERE id="%s"''' % message_id
		result = cursor.execute(query).fetchone()
		connection.close()
		return result


	def delete_messge(self, message_id: str):
		connection, cursor = self.__connect()
		query = '''DELETE FROM messages WHERE id= "%s"''' % message_id
		cursor.execute(query)
		connection.commit()
		connection.close()


	def bind_answer(self, from_user_id: int, to_user_id: int, message_id: str):
		connection, cursor = self.__connect() 
		query = '''INSERT INTO answers VALUES ("%i", "%i", "%s")''' % (
			from_user_id, to_user_id, message_id)

		cursor.execute(query)
		connection.commit()
		connection.close()


# Интерфейс между сессией и базой данных
# Основной задачей является исправление недостатка sqlite3, а именно отсутствия bool типа данных.
class SessionDatabaseInterface:
	def __init__(self, real_db):
		self._real_db = real_db

	# 
	def append_user(self, user: usertypes.User):
		usersaver = UserSaver(user)
		data = usersaver.get_data()
		# Замена True и False на 1 и 0 соответственно
		data['is_blocked'] = 1 if user.is_blocked() else 0
		# 
		self._real_db.append_user(data)


	def select_users_chat_id(self):
		return self._real_db.select_users_chat_id()


	def load_user_by_chat_id(self, chat_id: int):
		data = self._real_db.load_user_by_chat_id(chat_id)
		# Замена 1 и 0 на True и False соответственно 
		is_blocked = True if data[3] == 1 else False

		userloader = UserLoader((data[0], data[1], data[2], is_blocked, data[4]))
		user = userloader.get_user()

		return user


	def update_user_nickname_by_chat_id(self, chat_id: int, nickname: str):
		self._real_db.update_user_nickname_by_chat_id(chat_id, nickname)


	def update_user_block_status_by_chat_id(self, chat_id: int, status: str):
		status = 1 if(status == True) else 0
		self._real_db.update_user_block_status_by_chat_id(chat_id, status)


	def detele_user_by_chat_id(self, chat_id: int):
		self._real_db.detele_user_by_chat_id(chat_id)


# Интерфейс между чатом и базой данных
class ChatDatabaseInterface:
	def __init__(self, real_db):
		self._real_db = real_db


	def has_message(self, message_id: str):
		return self._real_db.has_message(message_id)


	def append_message(self, message: contents.Message):
		ms = MessageSaver(message)
		self._real_db.append_message(ms.get_data())


	def update_message(self, message: contents.Message):
		ms = MessageSaver(message)
		self._real_db.update_message(ms.get_data())


	def select_message(self, message_id: str):
		data = self._real_db.select_messge(message_id)
		ml = MessageLoader(data)
		# 
		return ml.get_message()


	def delete_message(self, message_id: str):
		self._real_db.delete_message(message_id)


	def bind_answer(self, from_user_id: int, to_user_id: int, message_id: str):
		self._real_db.bind_answer(from_user_id, to_user_id, message_id)


class UserLoader:
	def __init__(self, data: tuple):
		self._chat_id = data[0]
		self._username = data[1]
		self._status = data[2]
		self._is_blocked = data[3]
		self._nickname = data[4]


	@property
	def chat_id(self):
		return self._chat_id


	@property
	def username(self):
		return self._username 


	@property
	def nickname(self):
		return self._nickname 


	@property
	def status(self):
		return self._status


	@property
	def is_blocked(self):
		return self._is_blocked

	# 
	def get_user(self):
		if(self._status == 'visitor'):
			user = usertypes.Visitor(self._chat_id, self._username)

		if(self._status == 'moder'):
			user = usertypes.Moderator(self._chat_id, self._username)

		if(self._status == 'admin'):
			user = usertypes.Administrator(self._chat_id, self._username)
			
		if(self._nickname):
			user.set_nickname(self._nickname)

		if(self._is_blocked):
			user.block()

		return user


class UserSaver:
	def __init__(self, user: usertypes.User):
		self._user = user
		self._data = {}


	@property
	def chat_id(self):
		return self._user.chat_id


	@property
	def username(self):
		return self._user.username 


	@property
	def nickname(self):
		return self._user.nickname 


	@property
	def status(self):
		return self._user.status


	@property
	def is_blocked(self):
		return self._user.is_blocked()

	# 
	def get_data(self):
		self._data['chat_id'] = self._user.chat_id
		self._data['username'] = self._user.username
		self._data['status'] = self._user.status
		self._data['is_blocked'] = self._user.is_blocked
		self._data['nickname'] = self._user.nickname

		return self._data


class MessageLoader:
	def __init__(self, data: tuple):
		self._id = data[0]
		self._chat_id = data[1]
		self._message_id = data[2]
		self._username = data[3]
		self._message = data[4] # Для текстового сообщения это текст, для фото и документа их подпись
		self._type = data[5] # Типом сообщений могут быть: message, photo, document
		self._body = data[6]
		self._file_id = data[7] # Контентом является айди фотографии или файла
		self._responses = data[8]
		self._recipients_chat_id = self._select_chat_and_message_id(data[9])

	# 
	def _select_chat_and_message_id(self, data):
		results = []
		for item in data.split(';'):
			values = item.split(':')
			if(len(values) == 2):
				results.append(values)
		
		return results


	def get_message(self):
		if(self._type == 'message'):
			message = contents.Text(self._username, self._chat_id, 
				self._message_id, self._message)
			# 
			message.update(self._body)

		if(self._type == 'photo'):
			message = contents.Photo(self._username, self._chat_id, 
				self._message_id, self._file_id, self._message)

		if(self._type == 'document'):
			message = contents.Document(self._username, self._chat_id, 
				self._message_id, self._file_id, self._message)

		# FEXME Замена сгенерированого id сообщения на старый id сообщения  
		message.set_id(self._id)
		message.update(self._body)

		if(self._recipients_chat_id):
			for chat_and_message_id in self._recipients_chat_id:
				chat_id, message_id = chat_and_message_id
				
				message.add_recipient_chat_and_message_id(chat_id, message_id)

		# Накрутка ответов :D
		message.set_amount_responses(self._responses)

		return message


class MessageSaver:
	def __init__(self, message: contents.Message):
		self._message = message
		self._data = {}

	# 
	def _concatenate_chat_and_message_id(self):
		results = []
		recipients = self._message.get_recipients()
		for chat_id in recipients:
			results.append('%s:%s;' % (chat_id, recipients[chat_id]))

		return ''.join(results)


	def get_data(self):
		self._data['id'] = self._message.id
		self._data['chat_id'] = self._message.chat_id
		self._data['message_id'] = self._message.message_id
		self._data['username'] = self._message.username
		
		if(self._message.message):
			self._data['message'] = self._message.message
			self._data['type'] = 'message'
			self._data['file_id'] = None
		
		elif(self._message.photo_id):
			self._data['message'] = self._message.caption
			self._data['type'] = 'photo'
			self._data['file_id'] = self._message.photo_id

		elif(self._message.document_id):
			self._data['message'] = self._message.caption
			self._data['type'] = 'document'
			self._data['file_id'] = self._message.document_id

		self._data['body'] = self._message.body
		self._data['responses'] = self._message.amount_responses

		if(self._message.has_response()):
			self._data['recipients_chat_and_message_id'] = self._concatenate_chat_and_message_id()
		else:
			self._data['recipients_chat_and_message_id'] = ''

		return self._data
