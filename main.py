# -*- coding: utf-8 -*-
"""
Главный модуль GUI приложения Random Password Generator.
Автор: [Ваше Имя и Фамилия]
Версия: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
from password_logic import generate_password, save_to_history, load_history

class PasswordGeneratorApp:
    """
    Класс основного окна приложения Random Password Generator.
    """
    MIN_PASSWORD_LENGTH = 4
    MAX_PASSWORD_LENGTH = 64

    def __init__(self, master):
        self.master = master
        master.title("Random Password Generator")
        master.geometry("650x550")
        master.resizable(False, False)

        # --- Настройка стилей ---
        style = ttk.Style()
        style.theme_use('clam')

        # --- Элементы управления генерацией ---
        control_frame = ttk.LabelFrame(master, text="Настройки пароля", padding="10")
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Длина пароля
        ttk.Label(control_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.length_var = tk.IntVar(value=12)
        self.length_spinbox = ttk.Spinbox(
            control_frame, from_=self.MIN_PASSWORD_LENGTH, to=self.MAX_PASSWORD_LENGTH,
            textvariable=self.length_var, width=5, validate="focusout",
            validatecommand=(master.register(self.validate_length), '%P')
        )
        self.length_spinbox.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(control_frame, text=f"(от {self.MIN_PASSWORD_LENGTH} до {self.MAX_PASSWORD_LENGTH})").grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # Чекбоксы для типов символов
        self.digits_var = tk.BooleanVar(value=True)
        self.letters_var = tk.BooleanVar(value=True)
        self.specials_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(control_frame, text="Цифры (0-9)", variable=self.digits_var).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(control_frame, text="Буквы (A-Z, a-z)", variable=self.letters_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(control_frame, text="Спецсимволы (!\"#$%&...)", variable=self.specials_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Кнопка генерации
        self.generate_button = ttk.Button(control_frame, text="Сгенерировать пароль", command=self.on_generate_click)
        self.generate_button.grid(row=4, column=0, columnspan=3, pady=15)

        # Поле для отображения сгенерированного пароля
        result_frame = ttk.Frame(master)
        result_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ttk.Label(result_frame, text="Результат:").pack(side="left")
        self.result_var = tk.StringVar()
        self.result_entry = ttk.Entry(result_frame, textvariable=self.result_var, state="readonly", font=("Consolas", 12), width=40)
        self.result_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        # Кнопка копирования в буфер обмена
        self.copy_button = ttk.Button(result_frame, text="Копировать", command=self.copy_to_clipboard)
        self.copy_button.pack(side="left")

        # --- Таблица истории ---
        history_frame = ttk.LabelFrame(master, text="История генераций", padding="10")
        history_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Создаем Treeview для таблицы
        columns = ("timestamp", "password", "length", "options")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)

        # Определяем заголовки
        self.history_tree.heading("timestamp", text="Дата и Время")
        self.history_tree.heading("password", text="Пароль")
        self.history_tree.heading("length", text="Длина")
        self.history_tree.heading("options", text="Опции")

        # Определяем ширину столбцов
        self.history_tree.column("timestamp", width=140)
        self.history_tree.column("password", width=250)
        self.history_tree.column("length", width=50, anchor="center")
        self.history_tree.column("options", width=120)

        # Добавляем полосу прокрутки
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Кнопка очистки истории
        self.clear_button = ttk.Button(history_frame, text="Очистить историю", command=self.clear_history)
        self.clear_button.grid(row=1, column=0, pady=5)

        # Растягивание колонок при изменении размера
        master.columnconfigure(0, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)

        # Загружаем и отображаем историю при старте
        self.refresh_history_table()

    def validate_length(self, value):
        """
        Проверяет, что введённая длина пароля — целое число в допустимом диапазоне.
        Если нет — корректирует значение.
        """
        if value == "":
            return True
        try:
            length = int(value)
            if length < self.MIN_PASSWORD_LENGTH:
                self.length_var.set(self.MIN_PASSWORD_LENGTH)
            elif length > self.MAX_PASSWORD_LENGTH:
                self.length_var.set(self.MAX_PASSWORD_LENGTH)
            return True
        except ValueError:
            messagebox.showerror("Некорректный ввод", "Длина пароля должна быть целым числом.")
            self.length_var.set(12)  # Возвращаем значение по умолчанию
            return True

    def on_generate_click(self):
        """Обработчик нажатия на кнопку 'Сгенерировать пароль'."""
        try:
            length = self.length_var.get()
            use_digits = self.digits_var.get()
            use_letters = self.letters_var.get()
            use_specials = self.specials_var.get()

            # Вызов бизнес-логики
            password = generate_password(
                length=length,
                use_digits=use_digits,
                use_letters=use_letters,
                use_specials=use_specials
            )
            
            # Отображение результата
            self.result_var.set(password)

            # Сохранение в историю
            save_to_history(password, length, use_digits, use_letters, use_specials)
            # Обновление таблицы
            self.refresh_history_table()

        except ValueError as e:
            # Показываем ошибки валидации
            messagebox.showerror("Ошибка генерации", str(e))
        except Exception as e:
            messagebox.showerror("Непредвиденная ошибка", f"Произошла ошибка: {str(e)}")

    def copy_to_clipboard(self):
        """Копирует сгенерированный пароль в буфер обмена."""
        password = self.result_var.get()
        if password:
            self.master.clipboard_clear()
            self.master.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Пусто", "Сначала сгенерируйте пароль.")

    def refresh_history_table(self):
        """Загружает историю из JSON и заполняет таблицу."""
        # Очищаем таблицу
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Загружаем данные
        history = load_history()
        for entry in history:
            # Формируем строку опций
            options = []
            if entry.get("digits"): options.append("Цифры")
            if entry.get("letters"): options.append("Буквы")
            if entry.get("specials"): options.append("Спецсимволы")
            options_str = ", ".join(options)

            # Вставляем строку в таблицу
            self.history_tree.insert("", "end", values=(
                entry.get("timestamp", ""),
                entry.get("password", ""),
                entry.get("length", ""),
                options_str
            ))

    def clear_history(self):
        """Очищает историю после подтверждения пользователя."""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить всю историю паролей?"):
            try:
                # Просто перезаписываем файл пустым списком
                with open('history.json', 'w', encoding='utf-8') as f:
                    json.dump([], f)
                self.refresh_history_table()
                messagebox.showinfo("Готово", "История успешно очищена.")
            except Exception as e:
                messagebox.showerror("Ошибка файла", f"Не удалось очистить историю: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()
