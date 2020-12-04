from telebot import types


def make():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(types.InlineKeyboardButton(text="Начать", callback_data='ts'),
           types.InlineKeyboardButton(text="Завершить", callback_data=f'tf'))
    return kb