import telebot
from telebot import types
import json
from scripts import pay, license_adder
import re
from datetime import datetime
import calendar
import time

with open('scripts/config.json', 'r') as cfg:
    config = json.load(cfg)

bot = telebot.TeleBot(config['token'])
admin = config['admins']
admin_group = config['group']
staff = config['staff']
hosts = config['servers']
tech = config['tech']


@bot.message_handler(commands=['start'])
def start_cmd(message):
    if message.from_user.id in staff or message.chat.id == tech:
        if re.search('/start', message.text):
            start(message)


def start(message):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for host in hosts:
        button = types.InlineKeyboardButton(text=re.sub("https://", "", host),
                                            callback_data=f'server_{host}')
        kb.add(button)
    bot.send_message(message.chat.id,
                     'Выберите сервер',
                     reply_markup=kb)


@bot.callback_query_handler(lambda call: call.data == 'close')
def close(call):
    try:
        if call.from_user.id in staff or call.message.chat.id == tech:
            bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as exc:
        print(exc)


@bot.callback_query_handler(lambda call: re.search('server_', call.data))
def options(call):
    if call.from_user.id in staff or call.message.chat.id == tech:
        with open(f'cookies/{call.from_user.id}.cookie', 'w') as cookie:
            cookie.write(re.sub('server_', '', call.data))
        bot.send_message(call.message.chat.id,
                         'Выбери команду:'
                         '\n/updateaccess - Обновить доступ'
                         '\n/license - Обновить лицензии')


@bot.message_handler(commands=['updateaccess'])
def updateaccess_cmd(message):
    if message.from_user.id in staff and re.search('/updateaccess', message.text):
        kb = types.InlineKeyboardMarkup(row_width=6)
        now = datetime.now()
        now_year = now.year
        row = list()
        for i in range(0, 3):
            row.append(types.InlineKeyboardButton(text=now_year+i,
                                                  callback_data=f'year_{now_year+i}'))
        row.append(types.InlineKeyboardButton(text='Закрыть',
                                              callback_data='close'))
        kb.add(*row)
        bot.send_message(message.chat.id, 'Выберите год', reply_markup=kb)


@bot.callback_query_handler(lambda call: re.search(r'^year_', call.data))
def updateaccess_month(call):
    if call.from_user.id in staff:
        kb = types.InlineKeyboardMarkup(row_width=6)
        now = datetime.now()
        now_year = now.year
        row = list()
        year = re.sub(r'year_', '', call.data)

        if now_year == int(year):
            month = now.month
        else:
            month = 1
        for i in range(month, 13):
            row.append(types.InlineKeyboardButton(text=i, callback_data=f'month_{i}_{call.data}'))
        row.append(types.InlineKeyboardButton(text='Закрыть',
                                              callback_data='close'))
        kb.add(*row)
        bot.edit_message_text(f'{year}\nВыберите месяц', call.message.chat.id, call.message.message_id)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)


@bot.callback_query_handler(lambda call: re.search(r'^month_', call.data))
def updateaccess_day(call):
    if call.from_user.id in staff:
        kb = types.InlineKeyboardMarkup(row_width=6)
        month = re.search(r'(\d+)', re.sub(r'_year_(\d+$)', '', call.data)).group()
        year = re.search(r'(\d+$)', call.data).group()
        now = datetime.now()
        row = list()
        last_day = calendar.monthrange(int(year), int(month))[1]
        if int(month) == now.month and int(year) == now.year:
            first_day = now.day
        else:
            first_day = 1
        for i in range(first_day, last_day+1):
            row.append(types.InlineKeyboardButton(text=i,
                                                  callback_data=f'day_{i}.{month}.{year}'))
        row.append(types.InlineKeyboardButton(text='Закрыть',
                                              callback_data='close'))
        kb.add(*row)
        msg_text = f'{year} / {month}\nВыберите день'
        bot.edit_message_text(msg_text, call.message.chat.id, call.message.message_id)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)


@bot.callback_query_handler(lambda call: re.search(r'^day_', call.data))
def updateaccess_list(call):
    if call.from_user.id in staff:
        some_day = re.sub(r'day_', '', call.data)
        bot.send_message(call.message.chat.id, 'Отправте список')
        bot.register_next_step_handler(call.message, updateaccess_func, some_day)


def updateaccess_func(message, some_day):
    if message.from_user.id in staff:
        if message.text == '/start':
            start(message)
        elif message.text == '/updateaccess':
            updateaccess_cmd(message)
        else:
            userlist = message.text
            try:
                with open(f'cookies/{message.from_user.id}.cookie', 'r') as cookie:
                    host = cookie.read()
                    token = hosts[host]['token']
                try:
                    payments = pay.run(server=host, token=token, userlist=userlist, someday=some_day)
                    bot.send_message(message.chat.id, payments, parse_mode='HTML')
                except Exception as ex:
                    print(ex)
                    bot.send_message(message.chat.id, '*Wrong List!\nTry again*', parse_mode='markdown')
                    start(message)
            except FileNotFoundError:
                bot.send_message(message.chat.id, '*Change server first!*', parse_mode='markdown')
                start(message)


@bot.message_handler(commands=['license'])
def license_cmd(message):
    if message.chat.id == tech and re.search('/license', message.text):
        license_start(message)


def license_start(message):
    bot.send_message(message.chat.id, 'enter login')
    bot.register_next_step_handler(message, account_func)


def account_func(message):
    account = message.text
    try:
        with open(f'cookies/{message.from_user.id}.cookie', 'r') as cookie:
            host = cookie.read()
            token = hosts[host]['token']
            try:
                sid = license_adder.getacc(host, token, account)
            except Exception as exc:
                print(exc)
                sid = 'wrong'
            if sid == 'wrong':
                bot.send_message(message.chat.id, 'wrong login')
                start(message)
            else:
                bot.send_message(message.chat.id, 'how many?')
                bot.register_next_step_handler(message, license_func, sid)
    except FileNotFoundError as exc:
        print(exc)
        start(message)


def license_func(message, sid):
    add = message.text
    try:
        with open(f'cookies/{message.from_user.id}.cookie', 'r') as cookie:
            host = cookie.read()
            token = hosts[host]['token']
            try:
                add = int(add)
                if isinstance(add, int):
                    total = license_adder.adder(host, token, sid, add)
                    bot.send_message(message.chat.id, f'success {total}')
            except Exception as exc:
                print(exc)
                bot.send_message(message.chat.id, 'wrong adder')
                start(message)
    except FileNotFoundError as exc:
        print(exc)
        start(message)


if __name__ == '__main__':
    print('bot started!\npolling..')
    while True:
        try:
            bot.polling()
        except Exception as e:
            time.sleep(60)
            print(str(e))
