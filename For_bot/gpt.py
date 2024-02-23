import logging

import requests
import telebot
from telebot import types
import config
import nou
import json
from transformers import AutoTokenizer

bot = telebot.TeleBot(token=config.token)
answer = ''
user = {}
max_tokens_in_task = 2048
system_content = 'Ты - дружелюбный помощник! Давай подробный ответ на русском языке.'
task = ''
answer = ''
assistant_content = 'Ответь на вопрос:'

with open('user.json', 'w+') as file:
    json.dump(user, file)

def count_tokens(text):
    tokenizer = AutoTokenizer.from_pretrained("rhysjones/phi-2-orange")  # название модели
    return len(tokenizer.encode(text))



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
    if count_tokens(message.text) > max_tokens_in_task:
        bot.send_message(chat_id=message.chat.id, text="Сообщение слишком большое! Напиши вопрос короче")
        bot.register_next_step_handler_by_chat_id(message, get_promtss)
        return
    bot.send_message(chat_id=message.chat.id, text="Ожидай ответ!")
    bot.register_next_step_handler_by_chat_id(user_id, answer_function)
    # дальше идет обработка промта и отправка результата

@bot.message_handler(commands=['answer'])
def answer_function(call):
    user_id = call.message_id
    user_promt = user[user_id]['user_promt']
    answer = user[user_id]['answer']
    try:
        user[user_id]['resp'] = requests.post(
            'http://158.160.135.104:1234/v1/chat/completions',            #ПОМЕНЯТЬ
            headers={"Content-Type": "application/json"},

            json={
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_promt},
                    {"role": "assistant", "content": answer},
                ],
                "temperature": 1,
                "max_tokens": 2048
            }
        )
        if user[user_id]['resp'].status_code == 200 and 'choices' in user[user_id]['resp'].json():
            user[user_id]['result'] = user[user_id]['resp'].json()['choices'][0]['message']['content']

        keyboard = types.InlineKeyboardMarkup()
        button_1 = types.InlineKeyboardButton(text='Закончить', callback_data='button1')
        button_2 = types.InlineKeyboardButton(text='Продолжить генерацию', callback_data='button2')
        keyboard.add(button_1, button_2)
        bot.send_message(call.message.chat.id, text=user[user_id]['result'], reply_markup=keyboard)

        if call.data != 'button2':
            user[user_id]['user_promt'] = ''
            user[user_id]['answer'] = ''
            user_promt = ''
            answer = ''
            with open('user.json', 'w+') as file:
                json.dump(user, file)
            bot.register_next_step_handler(call, solve_task)
        else:
            user[user_id]['answer'] += user[user_id]['result']
            return
    except:
        logging.error(
            f"Не удалось сгенерировать, код состояния {user[user_id]['resp'].status_code}"
        )
        bot.reply_to(
            call,
            f"Извини, я не смог сгенерировать для тебя ответ сейчас",
        )


bot.polling()
