import telebot
from telebot import types
# Импорты
#=============================================================================
# Клавиотуры
class Keyboards:
 
    @staticmethod
    def menu():
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        kb.row(types.KeyboardButton("Быстрый скриншот"),  types.KeyboardButton("скриншот"))
        kb.row(types.KeyboardButton("Фото вебкамеры"),    types.KeyboardButton("Управление мышкой"))
        kb.row(types.KeyboardButton("Файлы и процессы"), types.KeyboardButton("Дополнительно"))
        kb.row(types.KeyboardButton("Информация"), types.KeyboardButton("уведомления"))
        kb.row(types.KeyboardButton("Диспетчер задач"))
        return kb
 
    @staticmethod
    def files():
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        kb.row(types.KeyboardButton("Запустить"),          types.KeyboardButton("Замочить процесс"))
        kb.row(types.KeyboardButton("⬇Скачать файл"), types.KeyboardButton("⬆Загрузить файл"))
        kb.row(types.KeyboardButton("Загрузить по ссылке"), types.KeyboardButton("Назад"))
        return kb
 
    @staticmethod
    def additionals():
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        kb.row(types.KeyboardButton("Выключить компьютер"),    types.KeyboardButton("Перезагрузить компьютер"))
        kb.row(types.KeyboardButton("Выполнить команду"),        types.KeyboardButton("Перейти по ссылке"))
        kb.row(types.KeyboardButton("О компьютере"),             types.KeyboardButton("Назад"))
        return kb
 
    @staticmethod
    def mouse():
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        kb.row(types.KeyboardButton("↖️"), types.KeyboardButton("⬆️"), types.KeyboardButton("↗️"))
        kb.row(types.KeyboardButton("⬅️"), types.KeyboardButton("🆗"), types.KeyboardButton("➡️"))
        kb.row(types.KeyboardButton("↙️"), types.KeyboardButton("⬇️"), types.KeyboardButton("↘️"))
        kb.row(types.KeyboardButton("Назад"), types.KeyboardButton("Указать размах курсора"))
        return kb
    
    @staticmethod
    def taskmanager():
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        kb.row(types.KeyboardButton("Все процессы"),      types.KeyboardButton("Топ по CPU"))
        kb.row(types.KeyboardButton("Топ по RAM"),        types.KeyboardButton("Состояние системы"))
        kb.row(types.KeyboardButton("Найти процесс"),     types.KeyboardButton("Завершить по PID"))
        kb.row(types.KeyboardButton("Назад"))
        return kb
# Клавиотуры
#====================================================================
# Местный config.py
INFO = """
ПРИВЕТ!
Я бот для управлением своим пк даже на расстоянии!
Что нужно? Только тг и интернет, ну и конечно же включеный пк"""
DB = "logs.db"
BOT_TOKEN = "TOKEN"
MY_ID = ID
MOUSE_MOVES = {
    #x y
    "⬆️": (0, -1),
    "⬇️": (0,  1),
    "⬅️": (-1, 0),
    "➡️": ( 1, 0),
    #диагонали x y
    "↗️": ( 1, -1),
    "↘️": ( 1, 1),
    "↖️": ( -1, -1),
    "↙️": ( -1, 1),
}
