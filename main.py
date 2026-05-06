import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# Глобальные переменные
favorites = []
favorites_file = "favorites.json"
results_listbox = None
favorites_listbox = None
search_entry = None
root = None
results_user_data = {}

def load_favorites():
    global favorites
    if os.path.exists(favorites_file):
        with open(favorites_file, 'r', encoding='utf-8') as f:
            try:
                favorites = json.load(f)
            except json.JSONDecodeError:
                favorites = []
    else:
        favorites = []

def save_favorites():
    with open(favorites_file, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, indent=4, ensure_ascii=False)

def load_favorites_to_listbox():
    global favorites_listbox
    favorites_listbox.delete(0, tk.END)
    for user in favorites:
        display_text = f"{user['login']} — 👤 {user.get('name', 'No name')} | 📍 {user.get('location', 'No location')}"
        favorites_listbox.insert(tk.END, display_text)

def show_user_info(user_data):
    info_win = tk.Toplevel(root)
    info_win.title(f"Информация о {user_data['login']}")
    info_win.geometry("500x400")

    text = f"""
    👤 Логин: {user_data['login']}
    📛 Имя: {user_data.get('name', 'Не указано')}
    🏢 Компания: {user_data.get('company', 'Не указана')}
    📍 Локация: {user_data.get('location', 'Не указана')}
    📅 Дата регистрации: {user_data.get('created_at', 'Неизвестно')[:10]}
    📊 Публичных репозиториев: {user_data.get('public_repos', 0)}
    👥 Подписчиков: {user_data.get('followers', 0)}
    🔗 Профиль: {user_data.get('html_url', 'Нет ссылки')}
    """

    tk.Label(info_win, text=text, font=("Courier", 10), justify=tk.LEFT).pack(pady=20, padx=20)

def on_user_select(event):
    global results_listbox, results_user_data
    selection = results_listbox.curselection()
    if not selection:
        return
    index = selection[0]
    display_text = results_listbox.get(index)
    user_data = results_user_data.get(display_text)
    if user_data:
        show_user_info(user_data)

def on_favorite_select(event):
    global favorites_listbox, favorites
    selection = favorites_listbox.curselection()
    if not selection:
        return
    index = selection[0]
    fav_data = favorites[index]
    show_user_info(fav_data)

def search_user():
    global search_entry, results_listbox, results_user_data
    username = search_entry.get().strip()
    
    if not username:
        messagebox.showwarning("Ошибка ввода", "Поле поиска не может быть пустым!")
        return

    results_listbox.delete(0, tk.END)
    results_user_data.clear()
    
    try:
        url = f"https://api.github.com/users/{username}"
        response = requests.get(url)

        if response.status_code == 200:
            user_data = response.json()
            display_text = f"{user_data['login']} — 👤 {user_data.get('name', 'No name')} | 📍 {user_data.get('location', 'No location')} | 📅 {user_data.get('created_at', 'Unknown')[:10]}"
            results_listbox.insert(tk.END, display_text)
            results_user_data[display_text] = user_data
        elif response.status_code == 404:
            messagebox.showerror("Не найдено", f"Пользователь '{username}' не найден на GitHub.")
        else:
            messagebox.showerror("Ошибка API", f"API вернул статус {response.status_code}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка сети", f"Не удалось подключиться к GitHub API: {e}")

def add_to_favorites():
    global results_listbox, results_user_data, favorites
    selection = results_listbox.curselection()
    
    if not selection:
        messagebox.showwarning("Нет выбора", "Сначала выберите пользователя из результатов поиска.")
        return

    index = selection[0]
    display_text = results_listbox.get(index)
    user_data = results_user_data.get(display_text)

    if not user_data:
        return

    # Проверка, не в избранном ли уже
    for fav in favorites:
        if fav['login'] == user_data['login']:
            messagebox.showinfo("Уже в избранном", f"{user_data['login']} уже добавлен в избранное.")
            return

    favorites.append(user_data)
    save_favorites()
    load_favorites_to_listbox()
    messagebox.showinfo("Добавлено", f"{user_data['login']} добавлен в избранное.")

def remove_from_favorites():
    global favorites_listbox, favorites
    selection = favorites_listbox.curselection()
    
    if not selection:
        messagebox.showwarning("Нет выбора", "Сначала выберите пользователя из избранного.")
        return

    index = selection[0]
    removed = favorites.pop(index)
    save_favorites()
    load_favorites_to_listbox()
    messagebox.showinfo("Удалено", f"{removed['login']} удалён из избранного.")

def clear_search():
    global search_entry, results_listbox, results_user_data
    search_entry.delete(0, tk.END)
    results_listbox.delete(0, tk.END)
    results_user_data.clear()

def create_widgets():
    global search_entry, results_listbox, favorites_listbox, root
    
    # Поле ввода
    tk.Label(root, text="Введите имя пользователя GitHub:", font=("Arial", 12)).pack(pady=10)
    search_entry = tk.Entry(root, width=50, font=("Arial", 12))
    search_entry.pack(pady=5)
    search_entry.bind("<Return>", lambda event: search_user())

    # Кнопка поиска
    search_btn = tk.Button(root, text="🔍 Поиск", command=search_user, bg="#2c3e50", fg="white", font=("Arial", 10))
    search_btn.pack(pady=5)

    # Результаты поиска
    tk.Label(root, text="Результаты поиска:", font=("Arial", 10, "bold")).pack(pady=10)
    results_listbox = tk.Listbox(root, height=10, font=("Arial", 10))
    results_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
    results_listbox.bind("<<ListboxSelect>>", on_user_select)

    # Избранное
    tk.Label(root, text="⭐ Избранные пользователи:", font=("Arial", 10, "bold")).pack(pady=10)
    favorites_listbox = tk.Listbox(root, height=6, font=("Arial", 10))
    favorites_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
    favorites_listbox.bind("<<ListboxSelect>>", on_favorite_select)

    load_favorites_to_listbox()

    # Кнопки управления
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    add_fav_btn = tk.Button(btn_frame, text="➕ Добавить в избранное", command=add_to_favorites, bg="#27ae60", fg="white")
    add_fav_btn.pack(side=tk.LEFT, padx=5)

    remove_fav_btn = tk.Button(btn_frame, text="❌ Удалить из избранного", command=remove_from_favorites, bg="#e74c3c", fg="white")
    remove_fav_btn.pack(side=tk.LEFT, padx=5)

    clear_btn = tk.Button(btn_frame, text="🗑️ Очистить поиск", command=clear_search, bg="#95a5a6", fg="white")
    clear_btn.pack(side=tk.LEFT, padx=5)

def main():
    global root
    root = tk.Tk()
    root.title("GitHub User Finder")
    root.geometry("700x600")
    root.resizable(False, False)
    
    load_favorites()
    create_widgets()
    
    root.mainloop()

if __name__ == "__main__":
    main()