import os
import time
import psutil
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))

FLAG = os.path.join(BASE, "tracker.flag")
PID = os.path.join(BASE, "tracker.pid")
GAMES = os.path.join(BASE, "games.txt")
SESSIONS = os.path.join(BASE, "sessions.txt")

# защита от двойного запуска
if os.path.exists(PID):
    exit()

# регистрируем процесс
with open(PID, "w") as f:
    f.write(str(os.getpid()))

# гарантируем файл сессий
if not os.path.exists(SESSIONS):
    with open(SESSIONS, "w", encoding="utf-8") as f:
        f.write("")

# загружаем список игр
def load_games():
    if not os.path.exists(GAMES):
        return set()
    with open(GAMES, "r", encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if line.strip())

games = load_games()
active_sessions = {}  # game -> start_timestamp

def write_session(game, start_ts):
    end_time = datetime.now()
    start_time = datetime.fromtimestamp(start_ts)
    duration = int(end_time.timestamp() - start_ts)

    h = duration // 3600
    m = (duration % 3600) // 60
    s = duration % 60

    date_str = end_time.strftime("%Y-%m-%d")
    start_str = start_time.strftime("%H:%M:%S")
    end_str = end_time.strftime("%H:%M:%S")

    # проверяем, есть ли уже заголовок дня
    need_header = True
    with open(SESSIONS, "r", encoding="utf-8") as r:
        if f"Дата: {date_str}" in r.read():
            need_header = False

    with open(SESSIONS, "a", encoding="utf-8") as f:
        if need_header:
            f.write("\n" + "=" * 40 + "\n")
            f.write(f"Дата: {date_str}\n")
            f.write("=" * 40 + "\n\n")

        f.write(f"[{start_str}] Игра: {game}\n")
        f.write(f"Начало : {start_str}\n")
        f.write(f"Конец  : {end_str}\n")
        f.write(f"Время  : {h:02} ч {m:02} мин {s:02} сек\n")
        f.write("-" * 40 + "\n\n")

try:
    while os.path.exists(FLAG):
        # получаем текущие процессы
        running = {
            p.info["name"].lower()
            for p in psutil.process_iter(["name"])
            if p.info["name"]
        }

        # старт игр
        for game in games:
            if game in running and game not in active_sessions:
                active_sessions[game] = time.time()

        # завершение игр
        for game in list(active_sessions.keys()):
            if game not in running:
                start_ts = active_sessions.pop(game)
                write_session(game, start_ts)

        time.sleep(2)

finally:
    # корректное завершение
    if os.path.exists(PID):
        os.remove(PID)
