# ==============================================================================
#                               TRUTH OR DARE GAME
# ==============================================================================
# Необхідно встановити бібліотеки:
# pip install tkinter
# pip install pillow
# pip install random
# pip install pygame
# pip install os

from tkinter import *
from PIL import Image, ImageTk
import random
import pygame.mixer
import os

# ============================== GLOBAL SETUP ==================================
pygame.mixer.init()

BG_COLOR = "#2E0854"
BUTTON_COLOR = "#FF6B6B"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#FFD700"

script_dir = os.path.dirname(os.path.abspath(__file__))
background_music_path = os.path.join(script_dir, "background_music.mp3")
click_sound_path = os.path.join(script_dir, "computer-mouse-click-352734.mp3")
background_img_path = os.path.join(script_dir, "background.jpg")

SOUND_ENABLED = True
click_sound = None

truth_seq_index, used_truths = 0, []
dare_seq_index, used_dares = 0, []
current_player_idx = 0
current_mode = "random"

# ============================== ЛОКАЛІЗАЦІЯ ===================================
LANGS = {
    "UA": {
        "title": "ПРАВДА ЧИ ДІЯ",
        "btn_random": "У випадковому порядку",
        "btn_group": "По черзі",
        "btn_add": "Додати",
        "btn_start": "Почати",
        "btn_truth": "Правда",
        "btn_dare": "Дія",
        "btn_done": "Готово",
        "btn_exit": "Вихід",
        "entry_prompt": "Введіть імена гравців:",
        "error_min": "Потрібно мінімум 2 гравці!",
        "game_prompt": "Правда чи Дія?",
        "exit_question": "Бажаєте вийти з гри?",
        "exit_yes": "Вийти",
        "file_truth": "Правда.txt",
        "file_dare": "Дія.txt"
    },
    "EN": {
        "title": "TRUTH OR DARE",
        "btn_random": "Random Order",
        "btn_group": "Sequential Order",
        "btn_add": "Add",
        "btn_start": "Start",
        "btn_truth": "Truth",
        "btn_dare": "Dare",
        "btn_done": "Done",
        "btn_exit": "Exit",
        "entry_prompt": "Enter players names:",
        "error_min": "At least 2 players required!",
        "game_prompt": "Truth or Dare?",
        "exit_question": "Do you want to exit?",
        "exit_yes": "Exit",
        "file_truth": "Truths.txt",
        "file_dare": "Dares.txt"
    }
}

current_lang = "UA"


# ================================ FUNCTIONS ===================================

def play_sound(sound):
    if SOUND_ENABLED and sound:
        try:
            sound.play()
        except pygame.error:
            pass


def play_background_music():
    if SOUND_ENABLED and background_music_path and os.path.exists(background_music_path):
        try:
            pygame.mixer.music.load(background_music_path)
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass


def change_language(lang):
    global current_lang
    current_lang = lang
    play_sound(click_sound)

    try:
        heading.config(text=LANGS[current_lang]["title"])
        Random_button.config(text=LANGS[current_lang]["btn_random"])
        Group_button.config(text=LANGS[current_lang]["btn_group"])
    except (NameError, TclError, AttributeError):
        pass

    try:
        head_lbl.config(text=LANGS[current_lang]["entry_prompt"])
        add_btn.config(text=LANGS[current_lang]["btn_add"])
        launch_btn.config(text=LANGS[current_lang]["btn_start"])
    except (NameError, TclError, AttributeError):
        pass

    try:
        Truth_button.config(text=LANGS[current_lang]["btn_truth"])
        Dare_button.config(text=LANGS[current_lang]["btn_dare"])
        Done_button.config(text=LANGS[current_lang]["btn_done"])
        Exit_button.config(text=LANGS[current_lang]["btn_exit"])
        update_turn_label()
    except (NameError, TclError, AttributeError):
        pass

    try:
        confirm_label.config(text=LANGS[current_lang]["exit_question"])
        exit_btn.config(text=LANGS[current_lang]["exit_yes"])
    except (NameError, TclError, AttributeError):
        pass


def update_turn_label():
    try:
        if players:
            p_idx = current_player_idx if current_mode == "group" else players.index(current_player_name)
            p_name = players[p_idx]
            label1.config(text=f"{p_name}, {LANGS[current_lang]['game_prompt']}")
    except (NameError, TclError, ValueError, AttributeError):
        pass


# ============================ GAMEPLAY FUNCTIONS ==============================

def truth_fun():
    global truth_seq_index
    play_sound(click_sound); file_name = LANGS[current_lang]["file_truth"]
    try:
        with open(file_name, "r", encoding="utf-8") as file: lines = [l.strip() for l in file.readlines() if l.strip()]
        while lines:
            text = lines[truth_seq_index % len(lines)] if current_mode == "group" else random.choice(lines)
            if text not in used_truths or len(used_truths) >= len(lines):
                if len(used_truths) >= len(lines): used_truths.clear()
                used_truths.append(text); label2.config(text=text); break
        if current_mode == "group": truth_seq_index += 1
    except FileNotFoundError: label2.config(text="File not found!")


def dare_fun():
    global dare_seq_index
    play_sound(click_sound); file_name = LANGS[current_lang]["file_dare"]
    try:
        with open(file_name, "r", encoding="utf-8") as file: lines = [l.strip() for l in file.readlines() if l.strip()]
        while lines:
            text = lines[dare_seq_index % len(lines)] if current_mode == "group" else random.choice(lines)
            if text not in used_dares or len(used_dares) >= len(lines):
                if len(used_dares) >= len(lines): used_dares.clear()
                used_dares.append(text); label2.config(text=text); break
        if current_mode == "group": dare_seq_index += 1
    except FileNotFoundError: label2.config(text="File not found!")


def done_fun():
    play_sound(click_sound)
    label2.config(text="")
    if current_mode == "group":
        next_player_group()
    else:
        start_game_random()


def exit_fun():
    global confirm_label, exit_btn
    play_sound(click_sound)
    for widget in [label1, label2, Truth_button, Dare_button, Done_button, Exit_button]:
        widget.grid_forget()

    confirm_label = Label(root, text=LANGS[current_lang]["exit_question"], font=("Bold", 20), fg="White", bg=BG_COLOR)
    confirm_label.place(relx=0.5, rely=0.4, anchor=CENTER)
    exit_btn = Button(root, text=LANGS[current_lang]["exit_yes"], command=root.quit, **button_style)
    exit_btn.place(relx=0.5, rely=0.6, anchor=CENTER)


# ============================ MODE LOGIC ======================================
players = []
current_player_name = ""


def start_game_random():
    global current_player_name
    if not players: return
    current_player_name = random.choice(players)
    show_game_ui()
    update_turn_label()


def next_player_group():
    global current_player_idx
    if current_player_idx >= len(players): current_player_idx = 0
    show_game_ui()
    update_turn_label()
    current_player_idx += 1


def show_game_ui():
    label1.grid(row=0, column=2, pady=15)
    label2.grid(row=1, column=2, pady=10)
    Truth_button.grid(row=2, column=0, padx=5, pady=10)
    Dare_button.grid(row=2, column=1, padx=5, pady=10)
    Done_button.grid(row=2, column=3, padx=5, pady=10)
    Exit_button.grid(row=2, column=4, padx=5, pady=10)


def mode_setup(mode):
    global current_mode, head_lbl, name_entry, add_btn, launch_btn, error_lbl
    play_sound(click_sound)
    current_mode = mode
    Random_button.destroy()
    Group_button.destroy()

    def add_p():
        val = name_entry.get()
        if val: players.append(val); name_entry.delete(0, END)

    def launch():
        if len(players) < 2:
            error_lbl.config(text=LANGS[current_lang]["error_min"])
        else:
            for w in [name_entry, head_lbl, add_btn, launch_btn, heading, error_lbl]: w.destroy()
            create_game_widgets()
            if current_mode == "group":
                next_player_group()
            else:
                start_game_random()

    # --- ЗМІНЕНО РОЗТАШУВАННЯ ТА КОЛІР ФОНУ ---
    head_lbl = Label(root, text=LANGS[current_lang]["entry_prompt"], fg="White", font=("Bold", 20), bg=BG_COLOR)
    head_lbl.place(relx=0.5, rely=0.45, anchor=CENTER)  # Опущено з 0.2 до 0.45

    name_entry = Entry(root, font=("Arial", 20))
    name_entry.place(relx=0.5, rely=0.55, anchor=CENTER)  # Опущено з 0.35 до 0.55

    add_btn = Button(root, text=LANGS[current_lang]["btn_add"], command=add_p, **button_style)
    add_btn.place(relx=0.4, rely=0.7, anchor=CENTER)  # Опущено з 0.5 до 0.7

    launch_btn = Button(root, text=LANGS[current_lang]["btn_start"], command=launch, **button_style)
    launch_btn.place(relx=0.6, rely=0.7, anchor=CENTER)  # Опущено з 0.5 до 0.7

    error_lbl = Label(root, text="", fg="red", bg=BG_COLOR)
    error_lbl.place(relx=0.5, rely=0.8, anchor=CENTER)  # Опущено з 0.6 до 0.8


confirm_label = exit_btn = head_lbl = name_entry = add_btn = launch_btn = None
error_lbl = label1 = label2 = Truth_button = Dare_button = Done_button = None
Exit_button = heading = Random_button = Group_button = None


def create_game_widgets():
    global label1, label2, Truth_button, Dare_button, Done_button, Exit_button
    label1 = Label(root, text="", fg="White", bg=BG_COLOR, font=("Bold", 30))
    label2 = Label(root, text="", fg="White", bg=BG_COLOR, font=("Arial", 18), wraplength=600)
    Truth_button = Button(root, text=LANGS[current_lang]["btn_truth"], command=truth_fun, **button_style)
    Dare_button = Button(root, text=LANGS[current_lang]["btn_dare"], command=dare_fun, **button_style)
    Done_button = Button(root, text=LANGS[current_lang]["btn_done"], command=done_fun, **button_style)
    Exit_button = Button(root, text=LANGS[current_lang]["btn_exit"], command=exit_fun, **button_style)
    for btn in [Truth_button, Dare_button, Done_button, Exit_button]:
        btn.bind("<Enter>", lambda e: e.widget.config(bg="#FF8E8E"))
        btn.bind("<Leave>", lambda e: e.widget.config(bg=BUTTON_COLOR))


# ============================== START SCREEN ==================================
root = Tk()
root.title("Truth Or Dare")
root.geometry("1000x500")

button_style = {
    "bg": BUTTON_COLOR, "fg": TEXT_COLOR, "font": ("Arial", 14, "bold"),
    "borderwidth": 0, "relief": "flat", "padx": 20, "pady": 10,
    "activebackground": "#FF8E8E", "activeforeground": TEXT_COLOR
}

try:
    bg_raw = Image.open(background_img_path).resize((1920, 1080), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(bg_raw)
    Label(root, image=bg_image).place(x=0, y=0, relwidth=1, relheight=1) # type: ignore
except (FileNotFoundError, AttributeError, Exception):
    root.configure(bg=BG_COLOR)

heading = Label(root, text=LANGS[current_lang]["title"], fg=ACCENT_COLOR, bg=BG_COLOR, font=("Impact", 70, "bold"),
                pady=20)
heading.place(relx=0.5, rely=0.2, anchor=CENTER)

Random_button = Button(root, text=LANGS[current_lang]["btn_random"], command=lambda: mode_setup("random"),
                       **button_style)
Group_button = Button(root, text=LANGS[current_lang]["btn_group"], command=lambda: mode_setup("group"), **button_style)
Random_button.place(relx=0.5, rely=0.5, anchor=CENTER)
Group_button.place(relx=0.5, rely=0.65, anchor=CENTER)

lang_frame = Frame(root, bg=BG_COLOR)
lang_frame.place(x=20, y=20)
Button(lang_frame, text="UA", command=lambda: change_language("UA"), font=("Arial", 10, "bold"), bg=ACCENT_COLOR,
       width=3).pack(side=LEFT, padx=2)
Button(lang_frame, text="EN", command=lambda: change_language("EN"), font=("Arial", 10, "bold"), bg=ACCENT_COLOR,
       width=3).pack(side=LEFT, padx=2)

play_background_music()
root.mainloop()