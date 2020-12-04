from staff_bot import bot
import re
import json
from datetime import datetime
from keyboards import assembly_keyboard


def run(message):
    if re.search('/assembly', message.text):
        kb = assembly_keyboard.make()

        bot.send_message(message.chat.id, 'Что сделать?', reply_markup=kb)

    #     print(message)
    #     bot.send_message(message.from_user.id, 'Начало монтажа\nВведите номер задачи')


def aget(call):
    # print(call)
    bot.send_message(call.message.chat.id, 'Введите номер задачи')
    bot.register_next_step_handler(call.message, aupdate)


def aset(message):
    print(message)
    pass


def aupdate(message):
    print(message)
    # try:
    #     task = int(message.text)
    #     status = {
    #         "s": 1,
    #         "ts": datetime.now()
    #     }
    #     with open(f'modules/status/{id}.json', 'r') as fp:
    #         j = json.load(fp)
    #     j[task] = status
    #     with open(f'modules/status/{id}.json', 'w') as fp:
    #         json.dump(j, fp)
    #     bot.send_message(message.chat.id, 'Зарегистрировано время начала задачи')
    #
    # except Exception as e:
    #     print(e.with_traceback())
    #     bot.send_message(message.chat.id, 'Введите номер задачи')
    #     bot.register_next_step_handler(message, get, id)
