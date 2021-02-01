import hashlib
import os
from abc import ABC



class Message(ABC):
	def __init__(self, username: str, chat_id: int):
		self._id = self._create_random_id()
		self._username = username
		self._chat_id = chat_id
		self._message = None
		self._caption = None
		self._photo_id = None
		self._document_id = None
		self._responses = 0
		self._recipients_chat_id = {}

	# Создание случайного айди сообщения
	def _create_random_id(self):
		random_bytes = os.urandom(256)
		result = hashlib.sha256(random_bytes).hexdigest()
		return result[::2]

	
	def get(self):
		return self


	@property
	def id(self):
		return self._id


	@property
	def type(self):
		return self._type


	@property
	def chat_id(self):
		return self._chat_id


	@property
	def message_id(self):
		return self._message_id

	# 
	@property
	def username(self):
		return self._username

	# 
	@property
	def message(self):
		return self._message


	@property
	def body(self):
		return self._body

	
	@property
	def photo_id(self):
		return None


	@property
	def document_id(self):
		return None


	@property
	def amount_responses(self):
		return self._responses

	
	def set_id(self, message_id):
		self._id = message_id


	def set_amount_responses(self, amount_responses):
		self._responses = amount_responses

	# 
	def has_response(self):
		return self._responses > 0

	# 
	def add_response(self):
		self._responses += 1

	# 
	def add_recipient_chat_and_message_id(self, chat_id: int, message_id: int):
		self._recipients_chat_id.update({chat_id: message_id})

	#
	def get_recipients(self):
		return self._recipients_chat_id

	# 
	def update(self, body):
		self._body = body


class Text(Message):
	def __init__(self, username: str, chat_id: int, message_id: int, message: str):
		super(Text, self).__init__(username, chat_id)
		self._message_id = message_id
		self._message = message
		self._body = message


class Photo(Message):
	def __init__(self, username: str, chat_id: int, message_id: int, photo_id: str, caption: str):
		super(Photo, self).__init__(username, chat_id)
		self._message_id = message_id
		self._photo_id = photo_id
		self._caption = caption
		self._body = caption


	@property
	def photo_id(self):
		return self._photo_id


	@property
	def caption(self):
		return self._caption
	

class Document(Message):
	def __init__(self, username: str, chat_id: int, message_id: int, document_id: str, caption: str):
		super(Document, self).__init__(username, chat_id)
		self._message_id = message_id
		self._document_id = document_id
		self._caption = caption
		self._body = caption


	@property
	def document_id(self):
		return self._document_id
	

	@property
	def caption(self):
		return self._caption
