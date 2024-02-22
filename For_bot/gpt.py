import telebot
from telebot import types
import config
import nou
import json

bot = telebot.TeleBot(token=config.token)
answer = ''
user = {}
max_tokens_in_task = 2048

with open('user.json', 'w+') as file:
    json.dump(user, file)


@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(commands=['about'])
def about_command(message):
    user_id = message.chat.id
    bot.send_message(user_id, text="Рад, что ты заинтересован_а! Мое предназначение — не оставлять тебя в "
                                   "одиночестве и всячески подбадривать!")


@bot.message_handler(commands=['help'])
def help_function(message):
    user_id = message.chat.id
    bot.send_message(user_id, text='С помощью команд: \n'
                                   '/solve_task - можно задать роль боту \n'
                                   '/continue - бот продолжит формулировать ответ')


@bot.message_handler(commands=['start'])
def start_function(message):
    user_name = message.from_user.first_name
    user_id = message.chat.id
    if user_id in user:
        bot.send_message(message.from_user.id, text=f"Приветствую тебя снова, {user_name}!")
        bot.register_next_step_handler(message.chat.id, solve_task)
        user[user_id]['user_promt'] = ''
        user[user_id]['answer'] = ''
        user[user_id]['result'] = ''
        user[user_id]['resp'] = ''
    else:
        bot.send_message(message.from_user.id, text=f"Приветствую тебя, {user_name}!")
        user[user_id] = {}
        user[user_id]['user_promt'] = ''
        user[user_id]['answer'] = ''
        user[user_id]['result'] = ''
        user[user_id]['resp'] = ''
        with open('user.json', 'w+') as file:
            json.dump(user, file)
        bot.register_next_step_handler_by_chat_id(message.chat.id, solve_task)


@bot.message_handler(commands=['solve_task'])
def solve_task(message):
    user_id = message.from_user.id
    bot.send_message(user_id, text="Следующим сообщением напиши вопрос")
    # регистрируем следующий "шаг"
    bot.register_next_step_handler_by_chat_id(user_id, get_promtss)


# обработка действий для состояния "Получение ответа"
def get_promtss(message):
    user_id = message.chat.id
    # убеждаемся, что получили текстовое сообщение, а не что-то другое
    if message.content_type != "text":
        bot.send_message(chat_id=message.chat.id, text="Отправь ответ текстовым сообщением")
        # регистрируем следующий "шаг" на эту же функцию
        bot.register_next_step_handler_by_chat_id(message, get_promtss)
        return
    # получаем сообщение, которое и будет промтом
    user[user_id]['user_promt'] = message.text
    with open('user.json', 'w+') as file:
        json.dump(user, file)
#    if message.text > max_tokens_in_task:
#        bot.send_message(chat_id=message.chat.id, text="Сообщение слишком большое! Напиши вопрос короче")
#        bot.register_next_step_handler_by_chat_id(message, get_promtss)
#        return
    bot.send_message(chat_id=message.chat.id, text="Промт принят!")
    bot.register_next_step_handler_by_chat_id(user_id, nou.answer_function)
    # дальше идет обработка промта и отправка результата


bot.polling()
