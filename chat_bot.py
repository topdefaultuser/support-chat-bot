# -*- coding: utf-8 -*-
import os
import sys
import random
import time

import telebot
import flask

import usertypes
import database
import panels
import utils
import contents

# pip install pytelegrambotapi --upgrade
# pip install pytelegramAPI


API_TOKEN = os.environ['TOKEN']

WEBHOOK_DOMAIN = 'https://0866f6ebac8e.ngrok.io'
WEBHOOK_HOST = '%s/%s/' % (WEBHOOK_DOMAIN, API_TOKEN)

WEBHOOK_LISTEN = 'localhost'
WEBHOOK_PORT = 8443

WEBHOOK_URL = "/%s/" % API_TOKEN


bot = telebot.TeleBot(API_TOKEN)
app = flask.Flask(__name__)


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''


@app.route(WEBHOOK_URL, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


class Handler:
	def __init__(self, sessions: utils.Session, chat: utils.Chat):
		Handler._session = sessions
		Handler._chat = chat
		Handler._admin_panel = None
		Handler._moder_panel = None

	
	@staticmethod
	def set_admin_panel(admin_panel):
		Handler._admin_panel = admin_panel

	
	@staticmethod
	def set_moder_panel(moder_panel):
		Handler._moder_panel = moder_panel
	
	# Обработка начала диалога
	@staticmethod
	@bot.message_handler(commands=['start'])
	def start_handler(message: telebot.types.Message):
		# Проверка наличия пользователя в сессии 
		if(not Handler._session.has_user_by_chat_id(message.chat.id)):
			# 
			Handler._session.append_user(usertypes.Visitor(message.chat.id, message.chat.first_name))

			bot.send_message(message.chat.id, '👋 Добро пожаловать в наш уютный диалог!')
	
		elif(Handler._session.is_user_visitor_by_chat_id(message.chat.id)):
			bot.send_message(message.chat.id, '👋 С возвращением')

		elif(Handler._session.is_user_moderator_by_chat_id(message.chat.id)):
			bot.send_message(message.chat.id, '✴️✴️ Вы модератор ✴️✴️', 
				reply_markup=Handler._moder_panel.menu())
		 
		elif(Handler._session.is_user_administrator_by_chat_id(message.chat.id)):
			bot.send_message(message.chat.id, '⚜️⚜️ Вы главный ⚜️⚜️', reply_markup=Handler._admin_panel.menu())
	
	# Обработка запроса на администрирование и модерирование
	@staticmethod
	@bot.message_handler(commands=['moder'])
	def requests_handler(message: telebot.types.Message):
		# Если небыло команды /start но пользователь написал сразу сообщение автоматически 'запускает' бота
		if(not Handler._session.has_user_by_chat_id(message.chat.id)):
			Handler.start_handler(message)

		if(Handler._session.is_user_administrator_by_chat_id(message.chat.id)):
			bot.send_message(message.chat.id, '⚜️⚜️ Вы главный ⚜️⚜️')

		elif(Handler._session.is_user_moderator_by_chat_id(message.chat.id)):
			bot.send_message(message.chat.id, '✴️✴️ Вы модератор ✴️✴️')

		elif(Handler._session.has_requests_by_chat_id(message.chat.id)):
			bot.send_message(message.chat.id, '⚠️ ⚠️ Запрос на рассмотрении ⚠️ ⚠️')

		elif(message.text == '/moder'):
			Handler._session.append_requests(message.chat.id, message.chat.first_name)
			bot.send_message(message.chat.id, '📫 Вы отправили заявку на модерирование, ожидайте подтверждение')

		else:
			bot.send_message(message.chat.id, '⚠️ К сожалению, что-то пошло не так.')	
	
	# Обрабатывает сообщения
	@staticmethod
	@bot.message_handler(content_types=['text', 'photo', 'document'])
	def text_handler(message: telebot.types.Message):
		# Если небыло команды /start но пользователь написал сразу сообщение автоматически 'запускает' бота
		if(not Handler._session.has_user_by_chat_id(message.chat.id)):
			Handler.start_handler(message)

		elif(Handler._session.is_user_blocked_by_chat_id(message.chat.id)):
			bot.send_message(message.chat.id, '‼️ Вы заблокированы ‼️')

		elif(message.text == '[ ♠️ Добавить модератора ♠️ ]'):
			if(Handler._session.is_user_administrator_by_chat_id(message.chat.id)):
				requests = Handler._session.export_requests()
				markup, body = Handler._admin_panel.adition_moderators(requests)
				bot.send_message(message.chat.id, body, reply_markup=markup)
			else:
				markup = panels.clearn_menu()
				bot.send_message(message.chat.id, '⚠ У вас нет прав на осуществление данной команды', reply_markup=markup)

		elif(message.text == '[ 💎 Все управляющие 💎 ]'):
			if(Handler._session.is_user_administrator_by_chat_id(message.chat.id)):
				managers = Handler._session.export_managers()
				markup, body = Handler._admin_panel.managers(managers)
				bot.send_message(message.chat.id, body, reply_markup=markup)
			else:
				markup = panels.clearn_menu()
				bot.send_message(message.chat.id, '⚠ У вас нет прав на осуществление данной команды', reply_markup=markup)

		elif(message.text == '[ 🔕 Черный список 🔕 ]'):
			if(Handler._session.is_user_administrator_by_chat_id(message.chat.id) or Handler._session.is_user_moderator_by_chat_id(message.chat.id)):
				blocked_users = Handler._session.export_blocked_users()
				markup, body = Handler._admin_panel.blacklist(blocked_users)
				bot.send_message(message.chat.id, body, reply_markup=markup)
			else:
				markup = panels.clearn_menu()
				bot.send_message(message.chat.id, '⚠ У вас нет прав на осуществление данной команды', reply_markup=markup)

		elif(message.text == '[ ⚙️ Состояние чата ⚙️ ]'):
			if(Handler._session.is_user_administrator_by_chat_id(message.chat.id) or Handler._session.is_user_moderator_by_chat_id(message.chat.id)):
				text = ''
				if(Handler._session.is_admin_chat_work):
					text += '\n✅ Модераторский чат включен'
				else:
					text += '\n🛑 Модераторский чат выключен'

				if(Handler._session.is_users_chat_work):
					text += '\n✅ Пользовательский чат включен'
				else:
					text += '\n🛑 Пользовательский чат выключен'

				bot.send_message(message.chat.id, text)
			else:
				markup = panels.clearn_menu()
				bot.send_message(message.chat.id, '⚠ У вас нет прав на осуществление данной команды', reply_markup=markup)

		elif(message.text in ('[ 🛑 Откл. пользовательский чат 🛑 ]', 
			'[ ✅ Вкл. пользовательский  чат ✅ ]', 
			'[ 🛑 Откл. модераторский чат 🛑 ]', 
			'[ ✅ Вкл. модераторский чат ✅ ]')):

			if(Handler._session.is_user_administrator_by_chat_id(message.chat.id)):
				if(message.text == '[ 🛑 Откл. пользовательский чат 🛑 ]'):
					Handler._session.disable_users_chat()

				if(message.text == '[ ✅ Вкл. пользовательский  чат ✅ ]'):
					Handler._session.enable_users_chat()

				if(message.text == '[ 🛑 Откл. модераторский чат 🛑 ]'):
					Handler._session.disable_admin_chat()

				if(message.text == '[ ✅ Вкл. модераторский чат ✅ ]'):
					Handler._session.enable_admin_chat()

				# Разсылка измененны
				for manager in Handler._session.export_managers():

					if(Handler._session.is_user_moderator_by_chat_id(manager.chat_id)):
						if(message.text == '[ 🛑 Откл. пользовательский чат 🛑 ]'):
							text = '🛑 Пользовательский чат выключен'
						
						elif(message.text == '[ ✅ Вкл. пользовательский  чат ✅ ]'):
							text = '✅ Пользовательский чат включен'

						elif(message.text == '[ 🛑 Откл. модераторский чат 🛑 ]'):
							text = '🛑 Модераторский чат выключен'

						elif(message.text == '[ ✅ Вкл. модераторский чат ✅ ]'):
							text = '✅ Модераторский чат включен'
						
						else:
							text = '⚠ Непредвиденая комманда'

						bot.send_message(manager.chat_id, text)
					
					# 
					elif(Handler._session.is_user_administrator_by_chat_id(manager.chat_id)):
						if(message.text == '[ 🛑 Откл. пользовательский чат 🛑 ]'):
							text = '🛑 Пользовательский чат выключен'
						
						elif(message.text == '[ ✅ Вкл. пользовательский  чат ✅ ]'):
							text = '✅ Пользовательский чат включен'

						elif(message.text == '[ 🛑 Откл. модераторский чат 🛑 ]'):
							text = '🛑 Модераторский чат выключен'

						elif(message.text == '[ ✅ Вкл. модераторский чат ✅ ]'):
							text = '✅ Модераторский чат включен'
						
						else:
							text = '⚠ Непредвиденая комманда'

						bot.send_message(manager.chat_id, text, reply_markup=Handler._admin_panel.menu())
					
					else:
						bot.send_message(manager.chat_id, '⚠ Вы решены свохи прав',
							reply_markup=panels.clearn_menu())
			else:
				bot.send_message(message.chat.id, '⚠ У вас нет прав на осуществление данной команды', 
					reply_markup=panels.clearn_menu())

		elif(Handler._session.is_user_manager_by_chat_id(message.chat.id)):
			if(Handler._session.is_admin_chat_work):
				# 
				nickname = Handler._session.get_user_nickname_by_chat_id(message.chat.id)
				# 
				if(message.text):
					message_wrapper = contents.Text(nickname, message.chat.id, message.message_id, message.text).get()

				if(message.photo):
					message_wrapper = contents.Photo(nickname, message.chat.id, 
						message.message_id, message.photo[-1].file_id, message.caption).get()

				if(message.document):
					message_wrapper = contents.Document(nickname, message.chat.id, 
						message.message_id, message.document.file_id, message.caption).get()

				Handler._chat.append_message(message_wrapper)

				# Рассылка пользовательского сообщения управляющим
				for visitor in Handler._session.export_visitors():
					Handler.process_manager_message(visitor.chat_id, message_wrapper)
			else:
				bot.send_message(message.chat.id, '⚠️ Администраторский чат отключен!')

		elif(Handler._session.is_user_visitor_by_chat_id(message.chat.id)):
			if(Handler._session.is_users_chat_work):
				# 
				if(message.text):
					message_wrapper = contents.Text(message.chat.first_name, message.chat.id, 
						message.message_id, message.text)

				if(message.photo):
					message_wrapper = contents.Photo(message.chat.first_name, message.chat.id, 
						message.message_id, message.photo[-1].file_id, message.caption)

				if(message.document):
					message_wrapper = contents.Document(message.chat.first_name, message.chat.id, 
						message.message_id, message.document.file_id, message.caption)

				# Рассылка пользовательского сообщения управляющим
				for manager in Handler._session.export_managers():
					Handler.process_user_message(manager.chat_id, message_wrapper)
				
				Handler._chat.append_message(message_wrapper)

			else:
				bot.send_message(message.chat.id, '⚠️ Чат отключен!')
		else:
			bot.send_message(message.chat.id, '⚠️ Непредвиденая комманда')

	# Функция рассылки сообщений
	@staticmethod
	def process_user_message(chat_id: int, message: contents.Message):
		message_id = message.message_id

		markup = Handler.make_markup(message)

		if(message.message):
			body = 'От пользователя: <b>%s</b>\n\n%s\n\n🔴 [ без ответа ]' % (message.username, message.message)

			callback_message = bot.send_message(chat_id, body, parse_mode='HTML', reply_markup=markup)

		if(message.photo_id):
			if(message.caption):
				body = 'От пользователя: <b>%s</b>\n\n%s\n\n🔴 [ без ответа ]' % (message.username, message.caption)
			else:
				body = 'От пользователя: <b>%s</b>\n\n🔴 [ без ответа ]' % message.username

			callback_message = bot.send_photo(chat_id, message.photo_id, 
				caption=body, parse_mode='HTML', reply_markup=markup)

		if(message.document_id):
			if(message.caption):
				body = 'От пользователя: <b>%s</b>\n\n%s\n\n🔴 [ без ответа ]' % (message.username, message.caption)
			else:
				body = 'От пользователя: <b>%s</b>\n\n🔴 [ без ответа ]' % message.username

			callback_message = bot.send_document(chat_id, message.document_id, 
				caption=body, parse_mode='HTML', reply_markup=markup)	
		# 
		message.update(body)
		# Добавление сообщению данных для дальнейшего изменения
		message.add_recipient_chat_and_message_id(chat_id, callback_message.message_id)


	@staticmethod
	def process_manager_message(chat_id: int, message: contents.Message):
		message_id = message.message_id

		markup = telebot.types.InlineKeyboardMarkup()

		if(message.message):
			body = 'От: <b>%s</b>\n\n%s\n\n' % (message.username, message.message)

			callback_message = bot.send_message(chat_id, body, parse_mode='HTML', reply_markup=markup)

		if(message.photo_id):
			if(message.caption):
				body = 'От: <b>%s</b>\n\n%s\n\n' % (message.username, message.caption)
			else:
				body = 'От: <b>%s</b>\n\n' % message.username

			callback_message = bot.send_photo(chat_id, message.photo_id, 
				caption=body, parse_mode='HTML', reply_markup=markup)

		if(message.document_id):
			if(message.caption):
				body = 'От: <b>%s</b>\n\n%s\n\n' % (message.username, message.caption)
			else:
				body = 'От: <b>%s</b>\n\n' % message.username

			callback_message = bot.send_document(chat_id, message.document_id, 
				caption=body, parse_mode='HTML', reply_markup=markup)

		# Добавление сообщению данных для дальнейшего изменения
		message.add_recipient_chat_and_message_id(chat_id, callback_message.message_id)


	@staticmethod
	def make_markup(message_wrapper: contents.Message):
		markup = telebot.types.InlineKeyboardMarkup()
		markup.add(
			telebot.types.InlineKeyboardButton('Ответов (%i)' % message_wrapper.amount_responses, 
				callback_data='reply?%s' % message_wrapper.id),
		 	telebot.types.InlineKeyboardButton('Написать', 
		 		callback_data='send?%s' % message_wrapper.id)
		)

		if(Handler._session.is_user_blocked_by_chat_id(message_wrapper.chat_id)):
			markup.add(
				telebot.types.InlineKeyboardButton('Разблокировать', 
					callback_data='unblock?%s' % message_wrapper.id)
			)
		
		else:
			markup.add(
				telebot.types.InlineKeyboardButton('Заблокировать', 
					callback_data='block?%s' % message_wrapper.id)
			)

		return markup


	@staticmethod
	def make_body(message: telebot.types.Message, message_wrapper: contents.Message):
		if(not message_wrapper.has_response()):
			text = message_wrapper.body
			nickname = Handler._session.get_user_nickname_by_chat_id(message.chat.id)
			text = text.replace('🔴 [ без ответа ]', '🔵 [ Ответил: <b>%s</b> ]:\n\n' % nickname)
			if(message.text):
				text += message.text
			if(message.photo):
				text += 'Отправил фото'
			if(message.document):
				text += 'Отправил файл'
		else:
			text = message_wrapper.body
			nickname = Handler._session.get_user_nickname_by_chat_id(message.chat.id)
			text += '\n\n🔵 [ Ответил: <b>%s</b> ]:\n\n' % nickname
			if(message.text):
				text += message.text
			if(message.photo):
				text += 'Отправил фото'
			if(message.document):
				text += 'Отправил файл'

		# Обновление тела сообщения
		message_wrapper.update(text)
		# 
		message_wrapper.add_response()

		admin_panel = Handler.make_markup(message_wrapper)

		return message_wrapper, admin_panel

	# Обработчик колбэков
	@staticmethod
	@bot.callback_query_handler(func=lambda callback: True)
	def callback_handler(callback: telebot.types.CallbackQuery):
		# Обработка пользовательского ввода
		def send_mail(message: telebot.types.Message, message_wrapper: contents.Message):
			if(message.text == '[ ⚠️ Отмена ⚠️ ]'):
				if(Handler._session.is_user_moderator_by_chat_id(message.chat.id)):
					bot.send_message(message.chat.id, '⚠️ Ответ отменен ⚠️', reply_markup=Handler._moder_panel.menu())
				# 
				elif(Handler._session.is_user_administrator_by_chat_id(message.chat.id)): 
					bot.send_message(message.chat.id, '⚠️ Ответ отменен ⚠️', reply_markup=Handler._admin_panel.menu())
				
				else:
					bot.send_message(message.chat.id, '⚠ Упс. что-то пошло не так', reply_markup=panels.clearn_menu())
			
			else:
				# Получение ника отвечающего
				nickname = Handler._session.get_user_nickname_by_chat_id(message.chat.id)
				# 
				if(message.text):
					answer = contents.Text(nickname, message.chat.id, message.message_id, message.text).get()

				if(message.photo):
					answer = contents.Photo(nickname, message.chat.id, 
						message.message_id, message.photo[-1].file_id, message.caption).get()

				if(message.document):
					answer = contents.Document(nickname, message.chat.id, 
						message.message_id, message.document.file_id, message.caption).get()
				# Сохранение ответа в базе данных 
				Handler._chat.append_message(answer)
				# Запись в таблицу answers уникального айди сообщения, айди модератора и пользователя
				# Можно использовать для анализа ответов модераторов
				Handler._chat.bind_answer(message.chat.id, message_wrapper.chat_id, answer.id)
				# Отправка сообщения его автору
				if(message.text):
					bot.send_message(message_wrapper.chat_id, 'От: <b>%s</b>\n\n%s' % (nickname, message.text), 
						reply_to_message_id=message_wrapper.message_id, parse_mode='HTML')
				
				if(message.photo):
					caption = '\n\n' + message.caption if(message.caption) else ''
					bot.send_photo(message_wrapper.chat_id, message.photo[-1].file_id, 
						caption='От: <b>%s</b>%s' % (nickname, caption), parse_mode='HTML')
				
				if(message.document):
					caption = '\n\n' + message.caption if(message.caption) else ''
					bot.send_document(message_wrapper.chat_id, message.document.file_id, 
						caption='От: <b>%s</b>%s' % (nickname, caption), parse_mode='HTML')

				if(Handler._session.is_user_moderator_by_chat_id(message.chat.id)):
					bot.send_message(message.chat.id, '☑️ Сообщение пользователю %s отправлено ☑️' % message_wrapper.username, 
						reply_markup=Handler._moder_panel.menu())
				# 
				elif(Handler._session.is_user_administrator_by_chat_id(message.chat.id)):
					bot.send_message(message.chat.id, '☑️ Сообщение пользователю %s отправлено ☑️' % message_wrapper.username, 
						reply_markup=Handler._admin_panel.menu())
				else:
					bot.send_message(message.chat.id, '☑️ Сообщение пользователю %s отправлено ☑️' % message_wrapper.username, 
						reply_markup=panels.clearn_menu())

		# Обработка пользовательского ввода
		def enter_text(message: telebot.types.Message, message_wrapper: contents.Message):
			if(message.text == '[ ⚠️ Отмена ⚠️ ]'):
				if(Handler._session.is_user_moderator_by_chat_id(message.chat.id)):
					bot.send_message(message.chat.id, '⚠️ Ответ отменен ⚠️', 
						reply_markup=Handler._moder_panel.menu())
				# 
				elif(Handler._session.is_user_administrator_by_chat_id(message.chat.id)):
					bot.send_message(message.chat.id, '⚠️ Ответ отменен ⚠️', 
						reply_markup=Handler._admin_panel.menu())
				else:
					bot.send_message(message.chat.id, '⚠ Упс. что-то пошло не так', 
						reply_markup=panels.clearn_menu())
			else:
				message_wrapper, admin_panel = Handler.make_body(message, message_wrapper)
				# Получение ника отвечающего
				nickname = Handler._session.get_user_nickname_by_chat_id(message.chat.id)
				# 
				if(message.text):
					answer = contents.Text(nickname, message.chat.id, message.message_id, message.text).get()

				if(message.photo):
					answer = contents.Photo(nickname, message.chat.id, 
						message.message_id, message.photo[-1].file_id, message.caption).get()

				if(message.document):
					answer = contents.Document(nickname, message.chat.id, 
						message.message_id, message.document.file_id, message.caption).get()
				# Обновление сообщения 
				print('update_message')
				Handler._chat.update_message(message_wrapper)
				# Сохранение ответа в базе данных 
				Handler._chat.append_message(answer)
				# Запись в таблицу answers уникального айди сообщения, айди модератора и пользователя
				# Можно использовать для анализа ответов модераторов
				Handler._chat.bind_answer(message.chat.id, message_wrapper.chat_id, answer.id)
				# Отправка ответа пользователю
				if(message.text):
					bot.send_message(message_wrapper.chat_id, 'От: <b>%s</b>\n\n%s' % (nickname, message.text), 
						reply_to_message_id=message_wrapper.message_id, parse_mode='HTML')
				
				if(message.photo):
					caption = '\n\n' + message.caption if(message.caption) else ''
					bot.send_photo(message_wrapper.chat_id, message.photo[-1].file_id, 
						caption='От: <b>%s</b>%s' % (nickname, caption), parse_mode='HTML')
				
				if(message.document):
					caption = '\n\n' + message.caption if(message.caption) else ''
					bot.send_document(message_wrapper.chat_id, message.document.file_id, 
						caption='От: <b>%s</b>%s' % (nickname, caption), parse_mode='HTML')
				
				# Сообщение изменяется только в тех, кто его получил
				for recipient in message_wrapper.get_recipients().items():
					chat_id, message_id = recipient
					if(message_wrapper.message):
						bot.edit_message_text(chat_id=chat_id, message_id=message_id, 
							text=message_wrapper.body, parse_mode='HTML', reply_markup=admin_panel)
					else:
						bot.edit_message_caption(chat_id=chat_id, message_id=message_id, 
							caption=message_wrapper.body, parse_mode='HTML', reply_markup=admin_panel)

				if(Handler._session.is_user_moderator_by_chat_id(message.chat.id)):
					bot.send_message(message.chat.id, '☑️ Ответ отправлен ☑️',
						reply_markup=Handler._moder_panel.menu())

				# 
				elif(Handler._session.is_user_administrator_by_chat_id(message.chat.id)):
					bot.send_message(message.chat.id, '☑️ Ответ отправлен ☑️', 
						reply_markup=Handler._admin_panel.menu())
				
				else:
					bot.send_message(message.chat.id, '⚠ Упс. что-то пошло не так', 
						reply_markup=panels.clearn_menu())

		# Ответ на сообщения
		if(callback.data.startswith('reply')):
			if(Handler._session.is_user_manager_by_chat_id(callback.message.chat.id)):
				message_id = callback.data[callback.data.index('?')+1:]
				if(Handler._chat.has_user_message(message_id)):
					# 
					message = Handler._chat.select_message(message_id)
					# 
					if(Handler._session.has_user_by_chat_id(message.chat_id)):
						bot.answer_callback_query(callback.id, '✅ Введите ответ для пользователя ✅')
						bot.send_message(callback.message.chat.id, 'Введите ответ для: %s' % message.username, reply_markup=panels.cancel_menu())
						bot.register_next_step_handler(callback.message, lambda handler: enter_text(handler, message))
					else:
						bot.send_message(callback.message.chat.id, '⚠️ Пользователь не найден')
				else:
					bot.send_message(callback.message.chat.id, '⚠️ Сообщение не найдено')
			else:
				# Отображается у пользователей лишённых прав модерирования
				bot.delete_message(callback.message.chat.id, callback.message.message_id)
				bot.send_message(callback.message.chat.id, '⚠️ Вы больше не можете отвечать на сообщения пользователей!', 
					reply_markup=panels.clearn_menu())
	
		# Отправление сообщения от администратора
		if callback.data.startswith('send'):
			if(Handler._session.is_user_manager_by_chat_id(callback.message.chat.id)):
				message_id = callback.data[callback.data.index('?')+1: ]
				if(Handler._chat.has_user_message(message_id)):
					# 
					message = Handler._chat.select_message(message_id)

					if(Handler._session.has_user_by_chat_id(message.chat_id)):
						bot.answer_callback_query(callback.id, '✅ Введите сообщение для пользователя ✅')
						bot.send_message(callback.message.chat.id, 'Введите сообщение для: %s' % message.username, 
							reply_markup=panels.cancel_menu())
						bot.register_next_step_handler(callback.message, lambda event: send_mail(event, message))
					else:
						bot.send_message(callback.message.chat.id, '⚠️ Пользователь не найден')
				else:
					bot.send_message(callback.message.chat.id, '⚠️ Сообщение не найдено')
			else:
				bot.delete_message(callback.message.chat.id, callback.message.message_id)
				bot.send_message(callback.message.chat.id, 'Вы больше не можете отвечать на сообщения пользователей!', 
					reply_markup=panels.clearn_menu())

		# Блокировка пользователя вызваная с панели сообщения
		if(callback.data.startswith('block')):
			if(Handler._session.is_user_manager_by_chat_id(callback.message.chat.id)):
				message_id = callback.data[callback.data.index('?')+1: ]
				if(Handler._chat.has_user_message(message_id)):
					# 
					message = Handler._chat.select_message(message_id)
					# 
					if(Handler._session.has_user_by_chat_id(message.chat_id)):
						# 
						Handler._session.block_user_by_chat_id(message.chat_id)
						bot.send_message(message.chat_id, '🚫 Вы заблокированы! 🚫')
						bot.answer_callback_query(callback.id, '✅  Пользователь заблокирован ✅')
						# 
						admin_panel = Handler.make_markup(message)
						# 
						bot.edit_message_reply_markup(chat_id=callback.message.chat.id, 
							message_id=callback.message.message_id, reply_markup=admin_panel)
						# Раcсылает уведомления админам
						for manager in Handler._session.export_managers():
							bot.send_message(manager.chat_id, '🚫 Пользователь %s заблокирован 🚫' % message.username)
					else:
						bot.send_message(callback.message.chat.id, '⚠️ Пользователь не найден')
				else:
					bot.send_message(callback.message.chat.id, '⚠️ Сообщение пользователя не найдено')
			else:
				bot.delete_message(callback.message.chat.id, callback.message.message_id)
				bot.send_message(callback.message.chat.id, '⚠️ Вы больше не являетесь модератором!', 
					reply_markup=panels.clearn_menu())

		# Разблокировка пользователя вызваная с панели сообщения
		if(callback.data.startswith('unblock')):
			if(Handler._session.is_user_manager_by_chat_id(callback.message.chat.id)):
				message_id = callback.data[callback.data.index('?')+1: ]
				if(Handler._chat.has_user_message(message_id)):
					# 
					message = Handler._chat.select_message(message_id)

					if(Handler._session.has_user_by_chat_id(message.chat_id)):

						if(Handler._session.is_user_blocked_by_chat_id(message.chat_id)):
							# 
							Handler._session.unblock_user_by_chat_id(message.chat_id)
							bot.send_message(message.chat_id, '✅ Вы разблокированы ✅')
							bot.answer_callback_query(callback.id, '✅ Пользователь разблокирован ✅')
							# 
							admin_panel = Handler.make_markup(message)
							# 
							if(message.message):
								bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, 
									text=message.body, parse_mode='HTML', reply_markup=admin_panel)
							else:
								bot.edit_message_caption(chat_id=chat_id, message_id=message_id, 
									caption=message.body, parse_mode='HTML', reply_markup=admin_panel)
							# Раcсылает уведомления модераторам
							for manager in Handler._session.export_managers():
								bot.send_message(manager.chat_id, '✅ Пользователь %s разблокирован ✅' % message.username)
						else:
							bot.send_message(callback.message.chat.id, '⚠️ Пользователь не заблокирован')
							# Изменяем пнопки на новые
							admin_panel = Handler.make_markup(message)
							# 
							bot.edit_message_reply_markup(chat_id=callback.message.chat.id, 
								message_id=callback.message.message_id, reply_markup=admin_panel)
					else:
						bot.send_message(callback.message.chat.id, '⚠️ Пользователь не найден')
				else:
					bot.send_message(callback.message.chat.id, '⚠️ Сообщение пользователя не найдено')
			else:
				bot.delete_message(callback.message.chat.id, callback.message.message_id)
				bot.send_message(callback.message.chat.id, 'Вы больше не являетесь модератором!', 
					reply_markup=panels.clearn_menu())
		
		# Раpблокировка пользователя вызваная с черного списка
		if(callback.data.startswith('blacklist')):
			if(Handler._session.is_user_manager_by_chat_id(callback.message.chat.id)):
				try:
					chat_id = int(callback.data[callback.data.index('?')+1: callback.data.index('&')])
				except(ValueError):
					bot.send_message(callback.message.chat.id, '🆘 Системная ошибка. Получено некорректный чат айди пользователя')
				
				username = callback.data[callback.data.index('&')+1: ]

				if(Handler._session.has_user_by_chat_id(chat_id)):
					if(Handler._session.is_user_blocked_by_chat_id(chat_id)):
						# 
						Handler._session.unblock_user_by_chat_id(chat_id)
						bot.send_message(chat_id, '✅ Вы разблокированы ✅')
						bot.answer_callback_query(callback.id, '✅ Пользователь разблокирован ✅')

						# Обновление панели черного списка 
						blocked_users = Handler._session.export_blocked_users()
						markup, body = Handler._admin_panel.blacklist(blocked_users)
						
						bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, 
							text=body, reply_markup=markup, parse_mode='HTML')

						# Раcсылает уведомления модераторам
						for manager in Handler._session.export_managers():
							bot.send_message(manager.chat_id, '✅ Пользователь %s разблокирован ✅' % username)
					else:
						bot.send_message(callback.message.chat.id, '⚠️ Пользователь не заблокирован')
				else:
					bot.send_message(callback.message.chat.id, '⚠️ Пользователь не найден')
			else:
				bot.delete_message(callback.message.chat.id, callback.message.message_id)
				bot.send_message(callback.message.chat.id, '⚠ Вы больше не являетесь модератором!', 
					reply_markup=panels.clearn_menu())

		# Добавление нового модератора
		if callback.data.startswith('add_moder'):
			try:
				chat_id = int(callback.data[callback.data.index('?')+1: callback.data.index('&')])
			except(ValueError):
				bot.send_message(callback.message.chat.id, '🆘 Произошла системная ошибка. Получен некорректный чат айди пользователя.')
			
			username = callback.data[callback.data.index('&')+1: ]

			# Отправление модераторской панели новому пользователю 
			bot.send_message(chat_id, '♠️ Теперь вы модератор! ♠️', reply_markup=Handler._moder_panel.menu())
			bot.answer_callback_query(callback.id, 'Модератор %s добавлен!' % username)
			bot.delete_message(callback.message.chat.id, callback.message.message_id)
			# Удаление запроса на модерирование
			Handler._session.delete_requests_by_chat_id(chat_id)
			# Удаление пользователя с сессии
			Handler._session.delete_user_by_chat_id(chat_id)
			# Добавление пользователя с правами модератора
			moderator = usertypes.Moderator(chat_id, username)
			# Установка никнейма
			moderator.set_nickname('Агент поддержки: %i' % random.randint(1111, 9999))
			# 
			Handler._session.append_user(moderator)

		# Удаление модератора
		if callback.data.startswith('delete'):
			try:
				chat_id = int(callback.data[callback.data.index('?')+1: callback.data.index('&')])
				username = callback.data[callback.data.index('&')+1: ]
			except(ValueError):
				bot.send_message(callback.message.chat.id, '🆘 Произошла системная ошибка. Получен некорректный чат айди пользователя.')
			
			else:
				if(Handler._session.is_user_administrator_by_chat_id(callback.message.chat.id)):
					# Зашита от случайной блокировки администратора
					if(Handler._session.is_user_administrator_by_chat_id(chat_id)):
						bot.answer_callback_query(callback.id, '🚫 Невозможно лишить своих прав администратора. 🚫')
					else:
						bot.delete_message(callback.message.chat.id, callback.message.message_id)
						bot.send_message(chat_id, '🚫 Вы были лишены своих прав 🚫', reply_markup=panels.clearn_menu())
						# Удаление модератора
						Handler._session.delete_user_by_chat_id(chat_id)
						# Добавление данных базового профиля
						Handler._session.append_user(usertypes.Visitor(chat_id, username))
						# Раcсылает уведомления модераторам
						for manager in Handler._session.export_managers():
							bot.send_message(manager.chat_id, '🚫 %s был лишен своих прав 🚫' % username)
				else:
					bot.answer_callback_query(callback.id, '⚠ У вас нет прав на осуществление данной команды')

		# Выход с черного списка
		if callback.data.startswith('back_to_menu'):
			try:
				if(Handler._session.is_user_administrator_by_chat_id(callback.message.chat.id)):
					bot.send_message(callback.message.chat.id, '✅ Вы в главном меню', 
						reply_markup=Handler._admin_panel.menu())
				# 
				elif(Handler._session.is_user_moderator_by_chat_id(callback.message.chat.id)):
					bot.send_message(callback.message.chat.id, '✅ Вы в главном меню', 
						reply_markup=Handler._moder_panel.menu())
				else:
					bot.send_message(message.chat.id, '⚠ Упс. что-то пошло не так', 
						reply_markup=panels.clearn_menu())
				
				bot.delete_message(callback.message.chat.id, callback.message.message_id)
			
			except(NameError, AttributeError):
				bot.send_message(callback.message.chat.id, '⚠️ Произошла системная ошибка')
			
			except Exception as exc:
				bot.send_message(callback.message.chat.id, '⚠️ Произошла непредвиденая ошибка: %s' % exc)


def main():
	os.chdir(os.path.dirname(sys.argv[0]))
	# Инициализация базы данных
	db = database.SQLiteDatabase('mydatabase.db')
	# Создание интерфейса типа: сессия - база данных. Session\Database Interface
	sdi = database.SessionDatabaseInterface(db)
	# Инициализация сессии и подключение базы данных к ней
	session = utils.Session(sdi)
	# Создание интерфейса типа: чат - база данных. Chat\Database Interface
	cdi = database.ChatDatabaseInterface(db)
	# Инициализация чата и подключение базы данных к нему 
	chat = utils.Chat(cdi)
	# Инициализация обработчика и передача ему объектов класса Session и Chat 
	handler = Handler(session, chat)
	# 
	handler.set_admin_panel(panels.AdminPanel(session))
	handler.set_moder_panel(panels.ModerPanel(session))

	if(WEBHOOK_DOMAIN != ''):
		bot.remove_webhook()
		time.sleep(1)
		bot.set_webhook(url=WEBHOOK_HOST)

		app.run(host=WEBHOOK_LISTEN, port=WEBHOOK_PORT, debug=True)

	else:
		bot.polling(none_stop=True, interval=0)


if(__name__ == '__main__'):
	main()