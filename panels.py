from abc import (ABC, abstractmethod)

from telebot import types



# Клавиатуры для разных типов пользователей
class BasePanel(ABC):
	def __init__(self, session):
		self._admin_chat = None
		self._users_chat = None
		self._session = session


	@abstractmethod
	def _panel(self):
		return None


	def menu(self):
		self._admin_chat = self._session.is_admin_chat_work
		self._users_chat = self._session.is_users_chat_work
		return self._panel()


	def enable_users_chat(self):
		self._users_chat = True


	def disable_users_chat(self):
		self._users_chat = False


	def enable_admin_chat(self):
		self._admin_chat = True


	def disable_admin_chat(self):
		self._admin_chat = True

# Панель для модератора
class ModerPanel(BasePanel):
	def _panel(self):
		options = types.ReplyKeyboardMarkup(resize_keyboard=True)
		options.add(types.KeyboardButton('[ ⚙️ Состояние чата ⚙️ ]'))
		options.add(types.KeyboardButton('[ 🔕 Черный список 🔕 ]'))
		return options

# Панель для администратора
class AdminPanel(BasePanel):
	def _panel(self):
		options = types.ReplyKeyboardMarkup(resize_keyboard=True)
		
		options.add(types.KeyboardButton('[ ⚙️ Состояние чата ⚙️ ]'))
		options.add(types.KeyboardButton('[ 🔕 Черный список 🔕 ]'))
		options.add(types.KeyboardButton('[ 💎 Все управляющие 💎 ]'))
		options.add(types.KeyboardButton('[ ♠️ Добавить модератора ♠️ ]'))

		if(self._users_chat):
			options.add(types.KeyboardButton('[ 🛑 Откл. пользовательский чат 🛑 ]'))
		else:
			options.add(types.KeyboardButton('[ ✅ Вкл. пользовательский  чат ✅ ]'))

		if(self._admin_chat):
			options.add(types.KeyboardButton('[ 🛑 Откл. модераторский чат 🛑 ]'))
		else:
			options.add(types.KeyboardButton('[ ✅ Вкл. модераторский чат ✅ ]'))

		return options

 
	@staticmethod
	def adition_moderators(data):
		markup = types.InlineKeyboardMarkup()
		if(len(data) == 0):
			message = '📢 Список запросов пуст!'
			markup.add(types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))

		else:
			message = '📫 Список запросов:'
			for chat_id in data:
				username = data[chat_id]
				markup.add(
					types.InlineKeyboardButton('🔹 Добавить: %s' % username, callback_data='add_moder?%s&%s' % (chat_id, username))
					)

			markup.add(types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))

		return (markup, message)


	@staticmethod
	def managers(managers: list):
		markup = types.InlineKeyboardMarkup()
		if(len(managers) == 0):
			message = '🤷‍♀️ Больше никого нет'
			markup.add(types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))

		else:
			message = 'Все модераторы:'
			for manager in managers:
				chat_id = manager.chat_id
				username = manager.username
				status = manager.status
				markup.add(
					types.InlineKeyboardButton('Удалить: ❌  %s    [%s]' % (username, status), 
						callback_data='delete?%s&%s' % (chat_id, username))
					)

			markup.add(types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))

		return (markup, message)


	@staticmethod
	def blacklist(blocked_users: list):
		markup = types.InlineKeyboardMarkup()
		if(len(blocked_users) == 0):
			message = '📢 Черный список пуст!'
			markup.add(types.InlineKeyboardButton('Назад', callback_data = 'back_to_menu'))

		else:
			message = '🔕 Черный список:'
			for user in blocked_users:
				chat_id = user.chat_id 
				username = user.username
				status = user.status
				
				markup.add(
					types.InlineKeyboardButton('Разблокировать: %s [%s]' % (username, status), 
						callback_data='blacklist?%s&%s' % (chat_id, username))
					)

			markup.add(types.InlineKeyboardButton('Назад', callback_data='back_to_menu'))

		return (markup, message)


def clearn_menu():
	return types.ReplyKeyboardRemove()


def cancel_menu():
	options = types.ReplyKeyboardMarkup(resize_keyboard=True)
	options.add(types.KeyboardButton('[ ⚠️ Отмена ⚠️ ]'))
	return options


if(__name__ == '__main__'):
	pass