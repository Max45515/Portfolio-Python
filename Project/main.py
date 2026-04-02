# 02.04.2026 создал телеграм бота на основе библиотек ниже (коментарии добавлены при помощи ИИ) 
# 04.02.2026 created a telegram bot based on the libraries below (comments added using AI)

import telebot
import sqlite3

# Инициализация бота с помощью токена
# Initialize the bot using the token
TOKEN = "" # use your token / используй свой токен
bot = telebot.TeleBot(TOKEN)

# Функция для работы с БД: создание таблицы и добавление задачи
# Function for database operations: table creation and adding a task
def add_task_to_db(user_id, task_text):
    # Устанавливаем соединение с файлом базы данных
    # Establish a connection with the database file
    conn = sqlite3.connect('User_Tasks.db')
    cursor = conn.cursor()
    try:
        # Создаем таблицу, если она еще не существует (ID, Пользователь, Текст задачи)
        # Create the table if it doesn't exist yet (ID, User, Task text)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS User_Tasks (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                User TEXT,
                Task TEXT
            )
        ''')
        # Записываем ID пользователя и текст его задачи в таблицу
        # Insert user ID and their task text into the table
        cursor.execute(
            "INSERT INTO User_Tasks (User, Task) VALUES (?, ?)", 
            (str(user_id), task_text)
        )
        # Фиксируем изменения в базе данных
        # Commit the changes to the database
        conn.commit()
    except sqlite3.Error as e:
        # Вывод ошибки в консоль, если что-то пошло не так
        # Print database error to console if something goes wrong
        print(f"Ошибка БД / DB Error: {e}")
    finally:
        # Обязательно закрываем соединение
        # Always close the connection
        conn.close()

# Обработчик команды /start: приветствие и инструкции
# Handler for /start command: greeting and instructions
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Привет! Чтобы добавить задачу, введи /add\n"
                          "Чтобы увидеть все задачи, введи /list\n"
                          "Чтобы очистить список, введи /clear")

# Обработчик команды /add: инициирует ввод новой задачи
# Handler for /add command: initiates new task input
@bot.message_handler(commands=["add"])
def add_task(message):
    # Запрашиваем текст задачи у пользователя
    # Ask the user for the task text
    msg = bot.reply_to(message, "Впиши текст задачи, которую нужно запомнить:")
    # Передаем управление функции save_user_task после того, как пользователь ответит
    # Register save_user_task as the next step after user reply
    bot.register_next_step_handler(msg, save_user_task)

# Функция сохранения текста задачи, полученного от пользователя
# Function to save task text received from the user
def save_user_task(message):
    user_input = message.text
    user_id = message.from_user.id

    # Вызываем функцию для записи данных в SQLite
    # Call the function to write data into SQLite
    add_task_to_db(user_id, user_input)
    
    bot.reply_to(message, f"✅ Задание добавлено в список:\n{user_input}")

# Обработчик команды /list: извлекает и показывает задачи пользователя
# Handler for /list command: fetches and displays user's tasks
@bot.message_handler(commands=["list"])
def show_task_list(message):
    conn = sqlite3.connect('User_Tasks.db')
    cursor = conn.cursor()

    user_id = str(message.from_user.id)
    # Выбираем все задачи, принадлежащие текущему пользователю
    # Select all tasks belonging to the current user
    cursor.execute("SELECT Task FROM User_Tasks WHERE User = ?", (user_id,))
    
    rows = cursor.fetchall()
    
    if not rows:
        response = "Твой список задач пуст!"
    else:
        # Собираем все строки из БД в одно сообщение с нумерацией
        # Format all DB rows into a single numbered message
        response = "Вот список твоих задач:\n" 
        for i, row in enumerate(rows, 1):
            response += f"{i}. {row[0]}\n"
    
    conn.close()
    bot.reply_to(message, response)

# Обработчик команды /clear: удаляет все задачи пользователя
# Handler for /clear command: deletes all user's tasks
@bot.message_handler(commands=["clear"])
def user_list_clear(message):
    conn = sqlite3.connect('User_Tasks.db')
    cursor = conn.cursor()
    user_id = str(message.from_user.id)

    # Проверяем наличие записей перед удалением
    # Check for existing records before deletion
    cursor.execute("SELECT 1 FROM User_Tasks WHERE User = ?", (user_id,))
    if not cursor.fetchone():
        bot.reply_to(message, "Твой список задач уже пуст!")
    else:
        # Удаляем все строки, где User совпадает с текущим
        # Delete all rows where User matches the current user
        cursor.execute("DELETE FROM User_Tasks WHERE User = ?", (user_id,))
        # Подтверждаем удаление (без этого данные останутся в БД)
        # Commit the deletion (mandatory to save changes)
        conn.commit()
        bot.reply_to(message, "Список задач полностью очищен!")

    conn.close()

# Точка входа в программу: запуск бота
# Entry point of the script: bot startup
if __name__ == '__main__':
    print("Бот запущен...") # Bot is running...
    bot.infinity_polling()
