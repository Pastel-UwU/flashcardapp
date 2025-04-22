import tkinter as tk
import sqlite3
from tkinter import ttk
from tkinter import messagebox
from ttkbootstrap import Style

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sets (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY,
            set_id INTEGER,
            word TEXT NOT NULL,
            definition TEXT NOT NULL,
            FOREIGN KEY (set_id) REFERENCES sets (id)
        )
    ''')

    def add_set(conn, set_name):
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO sets (name)
            VALUES (?)
        ''', (set_name,))

        set_id = cursor.lastrowid
        conn.commit()

        return set_id

if __name__ == '__main__':

    conn = sqlite3.connect('flashcards.db')
    create_tables(conn)

    root = tk.Tk()
    root.title("Flashcard App")
    root.geometry("700x500")

    style = Style(theme='superhero')
    style.configure('TLabel', font=('TkDefaultFont', 18))
    style.configure('TButton', font=('TkDefaultFont', 16))

    set_name_var = tk.StringVar()
    word_var = tk.StringVar()
    definition_var = tk.StringVar()

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    create_set_frame = ttk.Frame(notebook)
    notebook.add(create_set_frame, text="Create Set")

    ttk.Label(create_set_frame, text='Set Name:').pack(padx=5, pady=5)
    ttk.Entry(create_set_frame, textvariable=set_name_var, width=30).pack(padx=5, pady=5)

    ttk.Label(create_set_frame, text='Word:').pack(padx=5, pady=5)
    ttk.Entry(create_set_frame, textvariable=set_name_var, width=30).pack(padx=5, pady=5)

    ttk.Label(create_set_frame, text='Definition:').pack(padx=5, pady=5)
    ttk.Entry(create_set_frame, textvariable=set_name_var, width=30).pack(padx=5, pady=5)

    ttk.Button(create_set_frame, text='Create Set',).pack(padx=5, pady=10)
    ttk.Button(create_set_frame, text='Add Card',).pack(padx=5, pady=10)

    select_set_frame = ttk.Frame(notebook)
    notebook.add(select_set_frame, text="Select Set")

    sets_combobox = ttk.Combobox(select_set_frame, state='readonly')
    sets_combobox.pack(padx=5, pady=5)

    ttk.Button(select_set_frame, text='Select Set',).pack(padx=5, pady=5)
    ttk.Button(select_set_frame, text='Delete Set',).pack(padx=5, pady=5)

    flashcards_frame = ttk.Frame(notebook)
    notebook.add(flashcards_frame, text="Learn mode")

    card_index = 0
    current_tabs = []

    word_label = ttk.Label(flashcards_frame, text='', font=('TkDefaultFont', 24))
    word_label.pack(padx=5, pady=40)

    definition_label = ttk.Label(flashcards_frame, text='')
    definition_label.pack(padx=5, pady=5)

    ttk.Button(flashcards_frame, text='Flip').pack(side='left', padx=5, pady=5)
    ttk.Button(flashcards_frame, text='Next').pack(side='right', padx=5, pady=5)
    ttk.Button(flashcards_frame, text='Previous').pack(side='left', padx=5, pady=5)

    root.mainloop()