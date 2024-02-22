import config
import telebot
from telebot import types
import requests
import logging
import gpt
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)

bot = telebot.TeleBot(token=config.token)

system_content = 'Ты - дружелюбный помощник! Давай подробный ответ на русском языке.'
task = ''
answer = ''
assistant_content = 'Ответь на вопрос:'
max_tokens_in_task = 2048
user = {}

try:
    with open('user.json', 'r') as file:
        user = json.load(file)
except:
    user = {}


@bot.message_handler(commands=['answer'])
def answer_function(call):
    user_id = call.message_id
    try:
        user[user_id]['resp'] = requests.post(
            'http://158.160.135.104:1234/v1/chat/completions',            #ПОМЕНЯТЬ
            headers={"Content-Type": "application/json"},

            json={
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user[user_id]['user_promt']},
                    {"role": "assistant", "content": user[user_id]['answer']},
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
            with open('user.json', 'w+') as file:
                json.dump(user, file)
            bot.register_next_step_handler(call, gpt.solve_task)
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