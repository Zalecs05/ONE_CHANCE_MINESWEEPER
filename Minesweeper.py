import random
import sys
import tkinter as tk
import keyboard
import subprocess
import time

kolvo_flag = 0
cell = 40
hod = 0
rect_ids = {}
text_ids = {}
num_colors = {
    1: "#0000FF",   # синий
    2: "#008000",   # зелёный
    3: "#FF0000",   # красный
    4: "#000080",   # тёмно-синий
    5: "#800000",   # бордовый
    6: "#008080",   # бирюзовый
    7: "#000000",   # чёрный
    8: "#808080",   # серый
}
def look_for_click():
    canvas.bind("<Button-3>", right_handle_click)
    canvas.bind("<Button-1>", left_handle_click)
    root.mainloop()

def draw_cells(c, r, color, text = ""):
    x1, y1 = c * cell, r * cell
    x2, y2 = x1 + cell, y1 + cell
    rid = canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
    rect_ids[(r, c)] = rid
    if text:
        tid = canvas.create_text(x1 + cell / 2, y1 + cell / 2, text=text, font=("Arial", 16, "bold"))
        text_ids[(r, c)] = tid

def create_game(r, c):
    global gamepole, flags, opened
    gamepole = [[0 for i in range(dlina)] for j in range(visota)]
    opened = [[False for i in range(dlina)] for j in range(visota)]
    flags = [[False for i in range(dlina)] for j in range(visota)]
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
            if r == 0 and c == 0:
                if gamepole[r][c] == -1:
                    if gamepole[r+1][c] != -1:
                        gamepole[r+1][c] += 1
                    if gamepole[r][c+1] != -1:
                        gamepole[r][c+1] += 1
                    if gamepole[r+1][c+1] != -1:
                        gamepole[r+1][c+1] += 1
            elif r == 0 and c != dlina - 1:
                if gamepole[r][c] == -1:
                    if gamepole[r+1][c] != -1:
                        gamepole[r+1][c] += 1
                    if gamepole[r][c+1] != -1:
                        gamepole[r][c+1] += 1
                    if gamepole[r][c-1] != -1:
                        gamepole[r][c-1] += 1
                    if gamepole[r+1][c-1] != -1:
                        gamepole[r+1][c-1] += 1
                    if gamepole[r+1][c+1] != -1:
                        gamepole[r+1][c+1] += 1
            elif r == 0 and c == dlina - 1:
                if gamepole[r][c] == -1:
                    if gamepole[r+1][c] != -1:
                        gamepole[r+1][c] += 1
                    if gamepole[r][c-1] != -1:
                        gamepole[r][c-1] += 1
                    if gamepole[r+1][c-1] != -1:
                        gamepole[r+1][c-1] += 1
            elif r != visota - 1 and c == dlina - 1:
                if gamepole[r][c] == -1:
                    if gamepole[r-1][c] != -1:
                        gamepole[r-1][c] += 1
                    if gamepole[r+1][c] != -1:
                        gamepole[r+1][c] += 1
                    if gamepole[r-1][c-1] != -1:
                        gamepole[r-1][c-1] += 1
                    if gamepole[r][c-1] != -1:
                        gamepole[r][c-1] += 1
                    if gamepole[r+1][c-1] != -1:
                        gamepole[r+1][c-1] += 1
            elif r == visota - 1 and c == dlina - 1:
                if gamepole[r][c] == -1:
                    if gamepole[r-1][c] != -1:
                        gamepole[r-1][c] += 1
                    if gamepole[r-1][c-1] != -1:
                        gamepole[r-1][c-1] += 1
                    if gamepole[r][c-1] != -1:
                        gamepole[r][c-1] += 1
            elif r == visota - 1 and c != 0:
                if gamepole[r][c] == -1:
                    if gamepole[r][c-1] != -1:
                        gamepole[r][c-1] += 1
                    if gamepole[r][c+1] != -1:
                        gamepole[r][c+1] += 1
                    if gamepole[r-1][c-1] != -1:
                        gamepole[r-1][c-1] += 1
                    if gamepole[r-1][c] != -1:
                        gamepole[r-1][c] += 1
                    if gamepole[r-1][c+1] != -1:
                        gamepole[r-1][c+1] += 1
            elif r == visota - 1 and  c == 0:
                if gamepole[r][c] == -1:
                    if gamepole[r-1][c] != -1:
                        gamepole[r-1][c] += 1
                    if gamepole[r-1][c+1] != -1:
                        gamepole[r-1][c+1] += 1
                    if gamepole[r][c+1] != -1:
                        gamepole[r][c+1] += 1
            elif r != 0 and c == 0:
                if gamepole[r][c] == -1:
                    if gamepole[r-1][c] != -1:
                        gamepole[r-1][c] += 1
                    if gamepole[r+1][c] != -1:
                        gamepole[r+1][c] += 1
                    if gamepole[r-1][c+1] != -1:
                        gamepole[r-1][c+1] += 1
                    if gamepole[r][c+1] != -1:
                        gamepole[r][c+1] += 1
                    if gamepole[r+1][c+1] != -1:
                        gamepole[r+1][c+1] += 1
            else:
                if gamepole[r][c] == -1:
                    if gamepole[r-1][c-1] != -1:
                        gamepole[r-1][c-1] += 1
                    if gamepole[r][c-1] != -1:
                        gamepole[r][c-1] += 1
                    if gamepole[r+1][c-1] != -1:
                        gamepole[r+1][c-1] += 1
                    if gamepole[r-1][c] != -1:
                        gamepole[r-1][c] += 1
                    if gamepole[r+1][c] != -1:
                        gamepole[r+1][c] += 1
                    if gamepole[r-1][c+1] != -1:
                        gamepole[r-1][c+1] += 1
                    if gamepole[r][c+1] != -1:
                        gamepole[r][c+1] += 1
                    if gamepole[r+1][c+1] != -1:
                        gamepole[r+1][c+1] += 1

def left_handle_click(event):
    global hod
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
    global kolvo_flag
    r = event.y // cell
    c = event.x // cell
    if 0 <= r < visota and 0 <= c < dlina:
        print(f"Зафиксирован правый клик по {r}, {c}")
        if opened[r][c]:
            print("Ячейка уже открыта")
            return
        if max_flags == kolvo_flag:
            print("Слишком много флагов")
        if not (flags[r][c]) and max_flags != kolvo_flag and not(opened[r][c]):
            flags[r][c] = True
            redraw_cell(r, c, "#c0c0c0", "🚩")
            look_for_win()
            kolvo_flag += 1
        elif flags[r][c] and not(opened[r][c]):
            flags[r][c] = False
            redraw_cell(r, c, "#c0c0c0", "")
            look_for_win()
            kolvo_flag -= 1

def look_for_win():
    right_flags = 0
    open_cells = 0
    for r in range(visota):
        for c in range(dlina):
            if gamepole[r][c] == -1 and flags[r][c] == True:
                right_flags += 1
            if opened[r][c] and flags[r][c] == False:
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
    elif gamepole[r][c] == 0:
        redraw_cell(r, c, "#e0e0e0", "")
        if r == 0 and c == 0:
            open_cell(r+1, c)
            open_cell(r, c+1)
            open_cell(r+1, c+1)
        elif r != visota - 1 and c == 0:
            open_cell(r-1, c)
            open_cell(r+1, c)
            open_cell(r-1, c+1)
            open_cell(r, c+1)
            open_cell(r+1, c+1)
        elif r == visota - 1 and c == 0:
            open_cell(r-1, c)
            open_cell(r-1, c+1)
            open_cell(r, c+1)
        elif r == visota - 1 and c != dlina - 1:
            open_cell(r, c-1)
            open_cell(r-1, c-1)
            open_cell(r-1, c)
            open_cell(r-1, c+1)
            open_cell(r, c+1)
        elif r == visota - 1 and c == dlina - 1:
            open_cell(r, c-1)
            open_cell(r-1, c-1)
            open_cell(r-1, c)
        elif r != 0 and c == dlina - 1:
            open_cell(r, c-1)
            open_cell(r+1, c-1)
            open_cell(r-1, c-1)
            open_cell(r-1, c)
            open_cell(r+1, c)
        elif r == 0 and c == dlina - 1:
            open_cell(r, c-1)
            open_cell(r+1, c-1)
            open_cell(r+1, c)
        elif r == 0 and c != dlina - 1:
            open_cell(r, c-1)
            open_cell(r+1, c-1)
            open_cell(r+1, c)
            open_cell(r+1, c+1)
            open_cell(r, c+1)
        else:
            open_cell(r-1, c-1)
            open_cell(r, c-1)
            open_cell(r+1, c-1)
            open_cell(r-1, c)
            open_cell(r+1, c)
            open_cell(r-1, c+1)
            open_cell(r, c+1)
            open_cell(r+1, c+1)
    else:
        redraw_cell(r, c, "#e0e0e0", str(gamepole[r][c]), num_colors[gamepole[r][c]])

def redraw_cell(r, c, color, text="", text_color="black"):
    canvas.itemconfig(rect_ids[(r, c)], fill=color)
    if (r, c) in text_ids:
        canvas.delete(text_ids[(r, c)])
        del text_ids[(r, c)]
    if text:
        x1, y1 = c * cell, r * cell
        tid = canvas.create_text(x1 + cell / 2, y1 + cell / 2, text=text, font=("Arial", 16, "bold"), fill = text_color)
        text_ids[(r, c)] = tid

#def game():

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
            if not(opened[r][c]):
                open_cell(r, c)
    root.after(15000, root.destroy)

def keep_kiosk():
    try:
        root.attributes("-fullscreen", True)
        root.attributes("-topmost", True)
        root.lift()
        # root.focus_force()  # раскомментируй, если нужно постоянно забирать фокус
    finally:
        root.after(1000, keep_kiosk)


while True:
    #print("Введите длину поля (минимум 5)")
    dlina = 9
    if dlina < 5:
        #print("Неверная длина поля")
        continue
    else:
        break
while True:
    #print("Введите ширину поля (минимум 5)")
    visota = 9
    if visota < 5:
        #print("Неверная ширина поля")
        continue
    else:
        break
while True:
    #print(f"Сколько мин? (не больше чем {visota * dlina - 1})")
    kolvomin = 10
    if kolvomin > visota * dlina - 1 or kolvomin < 1:
        #print("Неверное кол-во мин")
        continue
    else:
        break
print("Генерация поля")
root = tk.Tk()
root.title("Сапёр")
root.attributes("-fullscreen", True)
#root.overrideredirect(True)
root.attributes("-topmost", True)
root.protocol("WM_DELETE_WINDOW", lambda: None)
for seq in ("<Alt-F4>", "<Escape>", "<Control-w>", "<Control-q>"):
    root.bind(seq, lambda e: "break")
canvas = tk.Canvas(
    root,
    width=dlina * cell,
    height=visota * cell,
    bg="#808080",
    highlightthickness=0
)
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
keyboard.add_hotkey("p", show_pole)
keyboard.add_hotkey("o", show_opened)
keyboard.add_hotkey("i", show_flags)
keyboard.add_hotkey("alt+f4", lambda: None, suppress=True)
keyboard.add_hotkey("ctrl+w", lambda: None, suppress=True)
keyboard.add_hotkey("ctrl+q", lambda: None, suppress=True)
keyboard.add_hotkey("ctrl+shift+esc", lambda: None, suppress=True)
keyboard.add_hotkey("win", lambda: None, suppress=True)
keyboard.add_hotkey("alt+space", lambda: None, suppress=True)
keyboard.add_hotkey("ctrl+alt+delete", lambda: None, suppress=True)
keyboard.add_hotkey("win+r", lambda: None, suppress=True)
keyboard.add_hotkey("ctrl+alt", lambda: None, suppress=True)
print("Поле заполнено")
print("Ожидаем первого хода")
look_for_click()
klik = 0
subprocess.Popen([sys.executable] + sys.argv)
sys.exit()
