import telebot
from telebot import types
import main
import bot
import json

bot = telebot.TeleBot(token=main.token)
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
    user_name = message.from_user.first_name
    if user_name in user:
         bot.send_message(message.from_user.id, text=f"Приветствую тебя снова, {user_name}!")
    else:
        bot.send_message(message.from_user.id, text=f"Приветствую тебя снова, {user_name}!")
        user[user_name] = ''
        user[user_name]['answer'] = ''
        user[user_name]['user_promt'] = ''
        with open('user.json', 'w+') as file:
            json.dump(user, file)
    bot.register_next_step_handler(message, solve_task)

@bot.message_handler(commands=['solve_task'])
def solve_task(message):
    user_id = message.from_user.id
    bot.send_message(user_id, text="Следующим сообщением напиши вопрос")
    # регистрируем следующий "шаг"
    bot.register_next_step_handler(message, bot.get_promt)