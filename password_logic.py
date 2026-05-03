# -*- coding: utf-8 -*-
"""
Модуль логики для приложения Random Password Generator.
Содержит функции для генерации пароля и управления историей в JSON-файле.
"""

import random
import string
import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"

def generate_password(length=12, use_digits=True, use_letters=True, use_specials=True):
    """
    Генерирует случайный пароль на основе заданных параметров.
    
    Args:
        length (int): Длина пароля (от 4 до 64).
        use_digits (bool): Включать ли цифры.
        use_letters (bool): Включать ли буквы (верхний и нижний регистр).
        use_specials (bool): Включать ли спецсимволы.
    
    Returns:
        str: Сгенерированный пароль.
    
    Raises:
        ValueError: Если длина вне диапазона или не выбран ни один тип символов.
    """
    # Валидация входных данных
    if not (4 <= length <= 64):
        raise ValueError("Длина пароля должна быть от 4 до 64 символов.")
    if not any([use_digits, use_letters, use_specials]):
        raise ValueError("Необходимо выбрать хотя бы один тип символов.")

    # Формируем пул символов для генерации
    character_pool = ""
    if use_digits:
        character_pool += string.digits
    if use_letters:
        character_pool += string.ascii_letters  # Включает строчные и прописные
    if use_specials:
        character_pool += string.punctuation  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

    # Генерация пароля с гарантированным включением хотя бы одного символа каждого выбранного типа
    password_chars = []
    if use_digits:
        password_chars.append(random.choice(string.digits))
    if use_letters:
        password_chars.append(random.choice(string.ascii_lowercase))
        password_chars.append(random.choice(string.ascii_uppercase))
    if use_specials:
        password_chars.append(random.choice(string.punctuation))

    # Дополнение до нужной длины случайными символами из общего пула
    remaining_length = length - len(password_chars)
    password_chars.extend(random.choice(character_pool) for _ in range(remaining_length))

    # Перемешивание для случайного порядка
    random.shuffle(password_chars)
    return "".join(password_chars)

def save_to_history(password, length, use_digits, use_letters, use_specials):
    """
    Сохраняет запись о сгенерированном пароле в JSON-файл истории.
    
    Args:
        password (str): Сам пароль.
        length (int): Запрошенная длина.
        use_digits (bool): Использовались ли цифры.
        use_letters (bool): Использовались ли буквы.
        use_specials (bool): Использовались ли спецсимволы.
    """
    history_entry = {
        "password": password,
        "length": length,
        "digits": use_digits,
        "letters": use_letters,
        "specials": use_specials,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Загружаем существующую историю или создаём новый список
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Если файл поврежден, начинаем с чистого листа
            history = []

    # Добавляем новую запись в начало списка, чтобы последние были сверху
    history.insert(0, history_entry)
    
    # Сохраняем обновленную историю
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def load_history():
    """
    Загружает и возвращает всю историю генерации паролей из JSON-файла.
    
    Returns:
        list: Список записей истории.
    """
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []
