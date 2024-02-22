import telebot
from telebot import types
import config
import nou
import json

bot = telebot.TeleBot(token=config.token)
answer = ''
user = {}

with open('user.json', 'w+') as file:
    json.dump(user, file)


@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)

@bot.message_handler(commands=['about'])
def about_command(message):
    bot.send_message(message.from_user.id, text="Рад, что ты заинтересован_а! Мое предназначение — не оставлять тебя в "
                                                "одиночестве и всячески подбадривать!")


@bot.message_handler(commands=['help'])
def help_function(message):
    bot.send_message(message.from_user.id, text='С помощью команд: \n'
                                                '/solve_task - можно задать роль боту \n'
                                                '/continue - бот продолжит формулировать ответ')

@bot.message_handler(commands=['start'])
def start_function(message):
    user_name = message.chat.id.first_name
    user_id = message.chat.id
    if user_id in user:
        bot.send_message(message.from_user.id, text=f"Приветствую тебя снова, {user_name}!")
        bot.register_next_step_handler(message, solve_task)
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
        bot.register_next_step_handler(message, solve_task)

@bot.message_handler(commands=['solve_task'])
def solve_task(message):
    user_id = message.from_user.id
    bot.send_message(user_id, text="Следующим сообщением напиши вопрос")
    # регистрируем следующий "шаг"
    bot.register_next_step_handler(user_id, nou.get_promtss)

bot.polling()