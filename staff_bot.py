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


@bot.message_handler(commands=['start'])
def start_cmd(message):
    if message.from_user.id in staff:
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


@bot.callback_query_handler(lambda call: re.search('server_', call.data))
def options(call):
    if call.from_user.id in staff:
        with open(f'cookies/{call.from_user.id}.cookie', 'w') as cookie:
            cookie.write(re.sub('server_', '', call.data))
        bot.send_message(call.message.chat.id, 'Change command:\n/updateaccess - Обновить доступ')


@bot.message_handler(commands=['updateaccess'])
def updateaccess_cmd(message):
    if message.from_user.id in staff and re.search('/updateaccess', message.text):
        kb = types.InlineKeyboardMarkup(row_width=6)
        now = datetime.now()
        now_year = now.year
        kb.row(types.InlineKeyboardButton(text=now_year, callback_data=f'year_{now_year}'),
               types.InlineKeyboardButton(text=now_year+1, callback_data=f'year_{now_year+1}'))
        bot.send_message(message.chat.id, 'Change year', reply_markup=kb)


@bot.callback_query_handler(lambda call: re.search('^year_', call.data))
def updateaccess_month(call):
    if call.from_user.id in staff:
        kb = types.InlineKeyboardMarkup(row_width=6)
        now = datetime.now()
        now_month = now.month
        row = list()
        for i in range(now_month, 13):
            row.append(types.InlineKeyboardButton(text=i, callback_data=f'month_{i}_{call.data}'))
        kb.add(*row)
        bot.edit_message_text('Change month', call.message.chat.id, call.message.message_id)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)


@bot.callback_query_handler(lambda call: re.search('^month_', call.data))
def updateaccess_day(call):
    if call.from_user.id in staff:
        kb = types.InlineKeyboardMarkup(row_width=6)
        month = re.search('(\d+)', re.sub('_year_(\d+$)', '', call.data)).group()
        year = re.search('(\d+$)', call.data).group()
        now = datetime.now()
        last_day = calendar.monthrange(int(year), int(month))[1]
        row = list()
        if int(month) == now.month:
            first_day = now.day
        else:
            first_day = 1

        for i in range(first_day, last_day+1):
            row.append(types.InlineKeyboardButton(text=i,
                                                  callback_data=f'day_{i}.{month}.{year}'))
        kb.add(*row)
        bot.edit_message_text('Change day', call.message.chat.id, call.message.message_id)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)


@bot.callback_query_handler(lambda call: re.search('^day_', call.data))
def updateaccess_list(call):
    if call.from_user.id in staff:
        some_day = re.sub('day_', '', call.data)
        bot.edit_message_text('Send list', call.message.chat.id, call.message.message_id)
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
                    print(payments)
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
    if message.from_user.id in staff and re.search('/license', message.text):
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
                id = license_adder.getacc(host, token, account)
            except Exception as e:
                print(e)
                id = 'wrong'
            if id == 'wrong':
                bot.send_message(message.chat.id, 'wrong login')
                license_start(message)
            else:
                bot.send_message(message.chat.id, 'how many?')
                bot.register_next_step_handler(message, license_func, id)
    except FileNotFoundError as e:
        print(e)
        start(message)


def license_func(message, id):
    add = message.text
    try:
        with open(f'cookies/{message.from_user.id}.cookie', 'r') as cookie:
            host = cookie.read()
            token = hosts[host]['token']
            try:
                add = int(add)
                if isinstance(add, int):
                    total = license_adder.adder(host, token, id, add)
                    bot.send_message(message.chat.id, f'success {total}')
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, 'wrong adder')
                license_start(message)
    except FileNotFoundError as e:
        print(e)
        start(message)


if __name__ == '__main__':
    print('bot started!\npolling..')
    while True:
        try:
            bot.polling()
        except Exception as e:
            time.sleep(60)
            print(str(e))
