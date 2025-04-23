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

def add_card(conn, set_id, word, definition):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cards (set_id, word, definition)
        VALUES (?, ?, ?)
    ''', (set_id, word, definition))
    card_id = cursor.lastrowid
    conn.commit()
    return card_id

def get_sets(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name FROM sets
    ''')
    rows = cursor.fetchall()
    sets = {row[1]: row[0] for row in rows}
    return sets

def create_set():
    set_name = set_name_var.get().strip()
    if not set_name:
        messagebox.showerror("Error", "Set name cannot be empty.")
        return

    if set_name in get_sets(conn):
        messagebox.showinfo("Info", f'The set "{set_name}" already exists.')
        return

    add_set(conn, set_name)
    populate_sets_combobox()
    set_name_var.set('')
    messagebox.showinfo("Success", f'Set "{set_name}" created successfully.')

def get_cards(conn, set_id):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT word, definition FROM cards
        WHERE set_id = ?
    ''', (set_id,))
    rows = cursor.fetchall()
    cards = [(row[0], row[1]) for row in rows]
    return cards

def delete_set(conn, set_id):
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM sets WHERE id = ?
    ''', (set_id,))
    cursor.execute('''
        DELETE FROM cards WHERE set_id = ?
    ''', (set_id,))
    conn.commit()
    sets_combobox.set('')
    clear_flashcard_display()
    populate_sets_combobox()

    global current_cards, card_index
    current_cards = []
    card_index = 0

def add_word():
    word = word_var.get()
    definition = definition_var.get()
    set_name = set_name_var.get()

    if set_name and word and definition:
        if set_name not in get_sets(conn):
            set_id = add_set(conn, set_name)
        else:
            set_id = get_sets(conn)[set_name]
        add_card(conn, set_id, word, definition)

        word_var.set('')
        definition_var.set('')
        populate_sets_combobox()

def populate_sets_combobox():
    sets_combobox['values'] = tuple(get_sets(conn).keys())

def delete_selected_set():
    set_name = sets_combobox.get()
    if set_name:
        result = messagebox.askyesno(
            'Confirmation', f'Are you sure you want to delete the set "{set_name}"?'
        )
        if result == tk.YES:
            set_id = get_sets(conn)[set_name]
            delete_set(conn, set_id)
            populate_sets_combobox()
            clear_flashcard_display()
            messagebox.showinfo("Success", f'Set "{set_name}" deleted successfully.')
    else:
        messagebox.showerror("Error", "No set selected to delete.")

def select_set():
    set_name = sets_combobox.get()
    if set_name:
        set_id = get_sets(conn)[set_name]
        cards = get_cards(conn, set_id)
        if cards:
            display_flashcards(cards)
        else:
            word_label.config(text='No cards available in this set.')
            definition_label.config(text='')
    else:
        global current_cards, card_index
        current_cards = []
        card_index = 0
        clear_flashcard_display()

def display_flashcards(cards):
    global card_index, current_cards
    card_index = 0
    current_cards = cards

    if not cards:
        clear_flashcard_display()
    else:
        show_card()

def clear_flashcard_display():
    word_label.config(text='')
    definition_label.config(text='')

def show_card():
    global card_index, current_cards

    if current_cards:
        if 0 <= card_index < len(current_cards):
            word, definition = current_cards[card_index]
            word_label.config(text=word)
            definition_label.config(text='')  # Clear the definition initially
        else:
            clear_flashcard_display()
    else:
        clear_flashcard_display()

def flip_card():
    global card_index, current_cards

    if current_cards:
        _, definition = current_cards[card_index]
        definition_label.config(text=definition)

def next_card():
    global card_index, current_cards

    if current_cards:
        card_index = (card_index + 1) % len(current_cards)
        show_card()

def prev_card():
    global card_index, current_cards

    if current_cards:
        card_index = (card_index - 1) % len(current_cards)
        show_card()

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
    set_id_var = tk.StringVar()

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    create_set_frame = ttk.Frame(notebook)
    notebook.add(create_set_frame, text="Create Set")

    ttk.Label(create_set_frame, text='Set Name:').pack(padx=5, pady=5)
    ttk.Entry(create_set_frame, textvariable=set_name_var, width=30).pack(padx=5, pady=5)

    ttk.Label(create_set_frame, text='Word:').pack(padx=5, pady=5)
    ttk.Entry(create_set_frame, textvariable=word_var, width=30).pack(padx=5, pady=5)

    ttk.Label(create_set_frame, text='Definition:').pack(padx=5, pady=5)
    ttk.Entry(create_set_frame, textvariable=definition_var, width=30).pack(padx=5, pady=5)

    ttk.Button(create_set_frame, text='Create Set', command=create_set).pack(padx=5, pady=10)
    ttk.Button(create_set_frame, text='Add Card', command=add_word).pack(padx=5, pady=10)

    select_set_frame = ttk.Frame(notebook)
    notebook.add(select_set_frame, text="Select Set")

    sets_combobox = ttk.Combobox(select_set_frame, state='readonly')
    sets_combobox.pack(padx=5, pady=5)
    sets_combobox.bind("<<ComboboxSelected>>", lambda event: select_set())

    ttk.Button(select_set_frame, text='Delete Set', command=delete_selected_set).pack(padx=5, pady=10)

    flashcards_frame = ttk.Frame(notebook)
    notebook.add(flashcards_frame, text="Learn mode")

    global word_label, definition_label

    word_label = ttk.Label(flashcards_frame, text='', font=('TkDefaultFont', 24))
    word_label.pack(padx=5, pady=40)

    definition_label = ttk.Label(flashcards_frame, text='')
    definition_label.pack(padx=5, pady=5)

    ttk.Button(flashcards_frame, text='Flip', command=flip_card).pack(side='left', padx=5, pady=5)
    ttk.Button(flashcards_frame, text='Next', command=next_card).pack(side='right', padx=5, pady=5)
    ttk.Button(flashcards_frame, text='Previous', command=prev_card).pack(side='left', padx=5, pady=5)

    root.mainloop()