from main import bot
from Data_Base_Crate import cursor
from Main_Button import button_message


@bot.message_handler(commands=['start'])  # Обрабатываем команду start
def start_message(message):
    cursor.execute(f"SELECT chat_id FROM user WHERE chat_id = '{message.chat.id}'")
    # Ищем id чата с которого нам написали

    if cursor.fetchone() is None:  # Если такой человек нам не писал, то к id его чата не привязано имя,
        # а значит мы не сможем заносить в бд его по имени,
        # тогда нам надо спросить его имя и привязать его к id его чата
        bot.send_message(message.chat.id,
                         "✌Привет\n"
                         "Я бот для заполнения РсОШ трекера\n\n"
                         "🔎Для начала надо зарегистрироваться")  # Основное приветствие
        bot.send_message(message.chat.id, "Напиши своё ФИО")  # Запрос ФИО

    else:  # Если id чата уже есть в бд, значит пользователь уже зарегистрирован, тогда
        bot.send_message(message.chat.id, "Привет, ты уже зарегистрирован")  # Приветствуем его и
        button_message(message)  # Выводим ему основное меню кнопок
