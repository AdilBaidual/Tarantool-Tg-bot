import time

import telebot
import sqlite3

bot = telebot.TeleBot('6019984780:AAE5EXixznM7MEVyc3xQT_YPXnZ9X06Iugs')


@bot.message_handler(commands=['start'])
def satrt(message):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute(
        'CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, login TEXT, password TEXT, service TEXT)')
    connection.commit()

    cursor.close()
    connection.close()


@bot.message_handler(commands=['set'])
def set_handler(message):
    if check_db():
        bot.send_message(message.chat.id, 'Введите login:')
        bot.register_next_step_handler(message, set_login)
    else:
        bot.send_message(message.chat.id, 'Введите /start')


def set_login(message):
    user_id = message.from_user.id
    login = message.text
    bot.send_message(message.chat.id, 'Введите password:')
    bot.register_next_step_handler(message, set_password, user_id, login)


def set_password(message, user_id, login):
    password = message.text
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.send_message(message.chat.id, 'Введите service:')
    bot.register_next_step_handler(message, set_service, user_id, login, password)


def set_service(message, user_id, login, password):
    service = message.text
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('INSERT INTO users(user_id, login, password, service) VALUES (?, ?, ?, ?)',
                   (user_id, login, password, service))
    connection.commit()

    cursor.close()
    connection.close()

    bot.send_message(message.chat.id, 'Данные сохранены')


@bot.message_handler(commands=['get'])
def get_handler(message):
    if check_db():
        bot.send_message(message.chat.id, "Введите сервис:")
        bot.register_next_step_handler(message, get_service)
    else:
        bot.send_message(message.chat.id, 'Введите /start')


def get_service(message):
    service = message.text
    user_id = message.from_user.id
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT login, password FROM users WHERE user_id = ? AND service = ?", (user_id, service))
    result = cursor.fetchone()
    if result:
        login, password = result
        tmp = bot.send_message(message.chat.id, f"Логин: {login}\nПароль: {password}")
        time.sleep(5)
        bot.delete_message(chat_id=message.chat.id, message_id=tmp.message_id)
    else:
        bot.send_message(message.chat.id, "Данные не найдены!")
    cursor.close()
    connection.close()


@bot.message_handler(commands=['del'])
def delete_service(message):
    if check_db():
        bot.send_message(message.chat.id, 'Введите service:')
        bot.register_next_step_handler(message, delete, message.from_user.id)
    else:
        bot.send_message(message.chat.id, 'Введите /start')


def delete(message, user_id):
    service = message.text
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=? AND service=?", (user_id, service))
    result = cursor.fetchone()
    if result is not None:
        cursor.execute("DELETE FROM users WHERE user_id=? AND service=?", (user_id, service))
        connection.commit()
        bot.reply_to(message, f"Запись для сервиса '{service}' успешно удалена.")
    else:
        bot.reply_to(message, f"Запись для сервиса '{service}' не найдена.")
    cursor.close()
    connection.close()


def check_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table_exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return table_exists


bot.polling(none_stop=True)
