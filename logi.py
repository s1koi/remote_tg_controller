import os
import sqlite3
import platform
import webbrowser
import ctypes
import mouse
import cv2
import PIL.ImageGrab
import requests
from PIL import Image, ImageDraw
from pySmartDL import SmartDL
from datetime import datetime
import psutil

from key import DB

#инит бд для логирования
def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                status   TEXT NOT NULL,
                function TEXT NOT NULL,
                message  TEXT,
                ts       TEXT NOT NULL
            )
        """)
        conn.commit()

#запись в логи
def log(status, function, message=""):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT INTO logs (status, function, message, ts) VALUES (?, ?, ?, ?)",
            (status, function, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()

#базовые настройки
class User:
    curs    = 50
    urldown = ""
    fin     = ""

#класс logic "бэкэнд" бота
class Logic:
    #скрин
    @staticmethod
    def get_screenshot():
        x, y = mouse.get_position()
        img = PIL.ImageGrab.grab()
        img.save("screen.png", "png")
        img = Image.open("screen.png")
        draw = ImageDraw.Draw(img)
        draw.polygon(
            (x, y, x, y + 20, x + 13, y + 13),
            fill="white", outline="black"
        )
        img.save("screen_with_mouse.png", "PNG")
        log("success", "get_screenshot")

    @staticmethod
    def cleanup_screenshot():
        for f in ("screen.png", "screen_with_mouse.png"):
            if os.path.exists(f):
                os.remove(f)

    #фото вебки

    @staticmethod
    def get_webcam_photo():
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        cv2.imwrite("webcam.png", frame)
        log("success", "get_webcam_photo")

    #управление мышью

    @staticmethod
    def move_mouse(dx, dy):
        x, y = mouse.get_position()
        mouse.move(x + dx, y + dy)
        log("success", "move_mouse", f"dx={dx} dy={dy}")

    @staticmethod
    def click_mouse():
        mouse.click()
        log("success", "click_mouse")

    @staticmethod
    def set_cursor_step(value):
        User.curs = int(float(value))
        log("success", "set_cursor_step", f"step={User.curs}")

    #Управление процессами

    @staticmethod
    def kill_process(name):
        os.system(f"taskkill /IM {name} /F")
        log("success", "kill_process", name)

    @staticmethod
    def start_file(path):
        os.startfile(path)
        log("success", "start_file", path)

    #Управление файлами

    @staticmethod
    def upload_file(file_name, file_bytes):
        with open(file_name, "wb") as f:
            f.write(file_bytes)
        log("success", "upload_file", file_name)
 
    @staticmethod
    def upload_by_url(url, save_path):
        obj = SmartDL(url, save_path, progress_bar=False)
        obj.start()
        log("success", "upload_by_url", f"{url} -> {save_path}")

    #Разные допы

    @staticmethod
    def open_url(url):
        webbrowser.open(url, new=0)
        log("success", "open_url", url)

    @staticmethod
    def run_cmd(command):
        os.system(command)
        log("success", "run_cmd", command)

    @staticmethod
    def shutdown():
        log("success", "shutdown")
        os.system("shutdown -s /t 0 /f")

    @staticmethod
    def reboot():
        log("success", "reboot")
        os.system("shutdown -r /t 0 /f")

    @staticmethod
    def get_pc_info():
        try:
            ip = requests.get("https://api.ipify.org", timeout=5).text
        except Exception:
            ip = "Недоступен"
        return (
            f"*Пользователь:* {os.getlogin()}\n"
            f"*IP:* {ip}\n"
            f"*ОС:* {platform.platform()}\n"
            f"*Процессор:* {platform.processor()}"
        )

    @staticmethod
    def show_msgbox(text):
        ctypes.windll.user32.MessageBoxW(None, text, "PC TOOL", 0)
        log("success", "show_msgbox", text)

class TaskManager:

    @staticmethod
    def _mb(bytes_val):
        return round(bytes_val / 1024 / 1024)

    @staticmethod
    def get_all_processes():
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        procs.sort(key=lambda x: x["name"].lower())
        log("success", "get_all_processes")

        lines = ["<b>📋 Все процессы:</b>\n"]
        for p in procs:
            ram = TaskManager._mb(p["memory_info"].rss) if p["memory_info"] else 0
            lines.append(f"<code>{p['pid']:<7}</code> {p['name'][:25]:<25} {ram}MB")

        #разрезание сообщения на части
        chunks = []
        chunk = ""
        for line in lines:
            if len(chunk) + len(line) + 1 > 3800:
                chunks.append(chunk)
                chunk = ""
            chunk += line + "\n"
        if chunk:
            chunks.append(chunk)
        return chunks
    #получение топа по cpu
    @staticmethod
    def get_top_cpu(n=10):
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        procs.sort(key=lambda x: x["cpu_percent"], reverse=True)
        log("success", "get_top_cpu")

        lines = [f"<b> Топ {n} по CPU:</b>\n"]
        for p in procs[:n]:
            ram = TaskManager._mb(p["memory_info"].rss) if p["memory_info"] else 0
            lines.append(
                f"<code>{p['pid']:<7}</code> {p['name'][:20]:<20} "
                f"CPU:{p['cpu_percent']}%  RAM:{ram}MB"
            )
        return "\n".join(lines)
    #получение топа по RAM
    @staticmethod
    def get_top_ram(n=10):
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        procs.sort(
            key=lambda x: x["memory_info"].rss if x["memory_info"] else 0,
            reverse=True
        )
        log("success", "get_top_ram")

        lines = [f"<b> Топ {n} по RAM:</b>\n"]
        for p in procs[:n]:
            ram = TaskManager._mb(p["memory_info"].rss) if p["memory_info"] else 0
            lines.append(
                f"<code>{p['pid']:<7}</code> {p['name'][:20]:<20} "
                f"RAM:{ram}MB  CPU:{p['cpu_percent']}%"
            )
        return "\n".join(lines)

    @staticmethod
    def get_system_stats():
        cpu    = psutil.cpu_percent(interval=1)
        ram    = psutil.virtual_memory()
        disk   = psutil.disk_usage("/")


        log("success", "get_system_stats")
        return (
            f"<b> Состояние системы:</b>\n\n"
            f"<b>CPU:</b> {cpu}%\n"
            f"<b>RAM:</b> {TaskManager._mb(ram.used)}MB / {TaskManager._mb(ram.total)}MB "
            f"({ram.percent}%)\n"
            f"<b>Диск C:</b> {TaskManager._mb(disk.used * 1024**2 // 1024**2)}MB использовано / "
            f"{round(disk.total / 1024**3)}GB всего ({disk.percent}%)"
        )
#поиск процесса
    @staticmethod
    def find_process(name):
        found = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
            try:
                if name.lower() in p.info["name"].lower():
                    found.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        log("success", "find_process", name)
 
        if not found:
            return f'Процессы с именем "{name}" не найдены'
 
        lines = [f'<b>🔍 Результат поиска "{name}":</b>\n']
        for p in found:
            ram = TaskManager._mb(p["memory_info"].rss) if p["memory_info"] else 0
            lines.append(
                f"<code>{p['pid']:<7}</code> {p['name'][:25]:<25} "
                f"CPU:{p['cpu_percent']}%  RAM:{ram}MB"
            )
        return "\n".join(lines)
#закрытие через pid
    @staticmethod
    def kill_by_pid(pid):
        try:
            p = psutil.Process(int(pid))
            name = p.name()
            p.kill()
            log("success", "kill_by_pid", f"pid={pid} name={name}")
            return f'Процесс {name} ({pid}) завершён'
        except psutil.NoSuchProcess:
            log("error", "kill_by_pid", f"PID {pid} не найден")
            return f'Процесс с {pid} не найден'
        except psutil.AccessDenied:
            log("error", "kill_by_pid", f"Нет доступа к PID {pid}")
            return f'Нет прав для завершения {pid}'

