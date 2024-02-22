import main
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

bot = telebot.TeleBot(token=main.token)

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

# обработка действий для состояния "Получение ответа"
def get_promt(message):
    user_name = message.from_user.id
    # убеждаемся, что получили текстовое сообщение, а не что-то другое
    if message.content_type != "text":
        bot.send_message(chat_id=message.chat.id, text="Отправь ответ текстовым сообщением")
        # регистрируем следующий "шаг" на эту же функцию
        bot.register_next_step_handler(message, get_promt)
        return
    # получаем сообщение, которое и будет промтом
    global user_promt
    user_promt = message.text
    user[user_name]['user_promt'] = user_promt

    user[user_name] = user_promt
    if message.text > max_tokens_in_task:
        bot.send_message(chat_id=message.chat.id, text="Сообщение слишком большое! Напиши вопрос короче")
        bot.register_next_step_handler(message, get_promt)
        return
    bot.send_message(chat_id=message.chat.id, text="Промт принят!")
    # дальше идет обработка промта и отправка результата

@bot.message_handler(commands=['answer'])
def answer_function(call):
    answer = ''
    global result
    user_name = call.from_user.first_name
    try:
        resp = requests.post(
            'http://localhost:1234/v1/chat/completions',            #ПОМЕНЯТЬ
            headers={"Content-Type": "application/json"},

            json={
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user[user_name]['user_promt']},
                    {"role": "assistant", "content": user[user_name]['answer']},
                ],
                "temperature": 1,
                "max_tokens": 2048
            }
        )
        if resp.status_code == 200 and 'choices' in resp.json():
            global result
            result = resp.json()['choices'][0]['message']['content']

        keyboard = types.InlineKeyboardMarkup()
        button_1 = types.InlineKeyboardButton(text='Закончить', callback_data='button1')
        button_2 = types.InlineKeyboardButton(text='Продолжить генерацию', callback_data='button2')
        keyboard.add(button_1, button_2)
        bot.send_message(call.message.chat.id, text=result, reply_markup=keyboard)

        if call.data != 'button2':
            user[user_name][user_promt] = ''
            global user
            user[user_name][answer] = ''
            bot.register_next_step_handler(call, gpt.solve_task)
        else:
            answer += result
            return
    except:
        logging.error(
            f"Не удалось получить изображение робота, код состояния {resp.status_code}"
        )
        bot.reply_to(
            call,
            "Извини, я не смог сгенерировать для тебя изображение робота прямо сейчас.",
        )

bot.polling()