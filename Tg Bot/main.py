import telebot
import sqlite3
from telebot import types
from Dicts import lessons_dict, mentors_dict, participation_stage_dict


def main():
    token = '5846254841:AAE9hO3V9sbtkOYZeODrCdoYKvVB1FscC1I'  # Токен бота
    bot = telebot.TeleBot(token)

    db = sqlite3.connect("Data_Bases//Users.db",
                         check_same_thread=False)  # Создаём бд с id чатов и какие имена к ним привязаны
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS user
                        (chat_id BIGINT,
                        user_name TEXT,
                        olympiad_index INT)
                    """)  # ID чата и какое имя ему принадлежит

    db_olympiad = sqlite3.connect("Data_Bases//RsOS.db",
                                  check_same_thread=False)  # Создаём бд с именами пользователей,
    # олимпиадой, которую он написал, предметом по которой писал олимпиаду, этап олимпиады и его наставником
    cursor_olymp = db_olympiad.cursor()
    cursor_olymp.execute("""CREATE TABLE IF NOT EXISTS olympiad
                            (user_name TEXT,
                            olympiad TEXT,
                            lesson TEXT,
                            participation_stage TEXT,
                            mentor TEXT)
                        """)

    olympiad_lst = []  # Список всех олимпиад
    olympiad_dict = {}  # Словарь, где ключ это индекс олимпиады, а значение это название олимпиады
    c = 0

    with open('Текстовые доки//РсОШ олимпиады.txt', 'r', encoding='utf-8') as file:
        olympiad = file.readlines()
        for i in olympiad:
            i = i.split(' - ')
            if i[0] not in olympiad_dict.keys():
                olympiad_dict[i[0]] = [i[1]]
            else:
                olympiad_dict[i[0]].append([i[1]])

    with open('Текстовые доки//РсОШ.txt', 'r', encoding='utf-8') as file:
        olympiad = file.readlines()
        string = ''
        for i in olympiad:
            if c <= 15:
                string += i + '\n'
                c += 1
            else:
                olympiad_lst.append(string)
                string, c = i + '\n', 0
        olympiad_lst.append(string)

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

    def name(message):  # Функция для регистрации пользователя
        fio = message.text  # Получаем ФИО пользователя

        cursor.execute(
            f"SELECT user_name FROM user WHERE user_name = '{fio}'")  # Проверяем, есть ли написанное имя в бд
        if cursor.fetchone() is None:  # Если его нет, тогда идём дальше
            cursor.execute('INSERT INTO user VALUES (?, ?, ?)',
                           (message.chat.id, message.text, 0))
            # Вписываем id чата пользователя и ФИО которое он написал
            db.commit()  # Сохраняем изменения в бд
            bot.send_message(message.chat.id,
                             "✅Ты успешно зарегистрировался")  # Оповещаем пользователя, что регистрация прошла успешно
            button_message(message)  # Выводим основное меню с кнопками
        else:  # Если имя уже есть, тогда
            bot.send_message(message.chat.id,
                             "❗️Пользователь с таким именем уже зарегистрирован")  # Говорим, что такое имя уже есть и
            button_message(message)  # Выводим основное меню с кнопками

    def button_message(message):  # Функция для вывода основного меню кнопок
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)  # Создаём меню

        new_olymp_register = types.KeyboardButton("✏️Зарегистрироваться на олимпиаду")
        my_olymp = types.KeyboardButton("📄Мои олимпиады")
        my_place = types.KeyboardButton("🏆Моё место в рейтинге")
        rename_user = types.KeyboardButton("🔃Поменять имя")
        olymp_statick = types.KeyboardButton("📊Статистика олимпиад")
        # new_register = types.KeyboardButton("Зарегистрировать нового пользователя")

        # Создаём основные кнопки

        markup.add(new_olymp_register, my_olymp, my_place, rename_user, olymp_statick)  # Добавляем кнопки в меню
        bot.send_message(message.chat.id, '❔Что тебя интересует?',
                         reply_markup=markup)  # Отправляем сообщение и выводим основное меню

    def receive_user_name(message):
        cursor.execute(f"SELECT user_name FROM user WHERE chat_id = '{message.chat.id}'")
        user_name = cursor.fetchone()[0]
        return user_name

    def send_olympiad_list(message, ind):  # Функция для вывода списка олимпиад
        keyboard = types.InlineKeyboardMarkup()
        next_15 = types.InlineKeyboardButton(text="➡️Следующие 15", callback_data='next_15')
        past_15 = types.InlineKeyboardButton(text="⬅️Прошлые 15", callback_data='past_15')
        pick_olympiad = types.InlineKeyboardButton(text="✍️Выбрать олимпиаду", callback_data='pick_olympiad')

        # print(ind, len(olympiad_lst) - 1)
        if ind != len(olympiad_lst) - 1 and ind != 0:
            keyboard.add(past_15, next_15)
        elif ind == 0:
            keyboard.add(next_15)
        elif ind == len(olympiad_lst) - 1:
            keyboard.add(past_15)

        keyboard.add(pick_olympiad)
        bot.send_message(message.chat.id, olympiad_lst[ind], reply_markup=keyboard)

    def pick_olymp(message):
        if message.text != '43':
            global name_user
            name_user = receive_user_name(message)
            pick_lesson(message)
        else:
            pass

    def pick_lesson(message):
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        lesson1 = types.InlineKeyboardButton(text="Астрономия (3)", callback_data='lesson1')
        lesson2 = types.InlineKeyboardButton(text="Биология (9)", callback_data='lesson2')
        lesson3 = types.InlineKeyboardButton(text="Генетика (2)", callback_data='lesson3')
        lesson4 = types.InlineKeyboardButton(text="География (9)", callback_data='lesson4')
        lesson5 = types.InlineKeyboardButton(text="Геология (2)", callback_data='lesson5')
        lesson6 = types.InlineKeyboardButton(text="Гуманитарные и социальные науки (3)", callback_data='lesson6')
        lesson7 = types.InlineKeyboardButton(text="Естественные науки (3)", callback_data='lesson7')
        lesson8 = types.InlineKeyboardButton(text="Журналистика (5)", callback_data='lesson8')
        lesson9 = types.InlineKeyboardButton(text="Инженерные науки(3)", callback_data='lesson9')
        lesson10 = types.InlineKeyboardButton(text="Иностранный язык (13)", callback_data='lesson10')
        lesson11 = types.InlineKeyboardButton(text="Информатика (14)", callback_data='lesson11')
        lesson12 = types.InlineKeyboardButton(text="Информационная безопасность (2)", callback_data='lesson12')
        lesson13 = types.InlineKeyboardButton(text="История (17)", callback_data='lesson13')
        lesson14 = types.InlineKeyboardButton(text="Лингвистика (2)", callback_data='lesson14')
        lesson15 = types.InlineKeyboardButton(text="Литература (7)", callback_data='lesson15')
        lesson16 = types.InlineKeyboardButton(text="Математика (27)", callback_data='lesson16')
        lesson17 = types.InlineKeyboardButton(text="Обществознание (13)", callback_data='lesson17')
        lesson18 = types.InlineKeyboardButton(text="Политология", callback_data='lesson18')
        lesson19 = types.InlineKeyboardButton(text="Право (7)", callback_data='lesson19')
        lesson20 = types.InlineKeyboardButton(text="Психология (2)", callback_data='lesson20')
        lesson21 = types.InlineKeyboardButton(text="Рисунок (2)", callback_data='lesson21')
        lesson22 = types.InlineKeyboardButton(text="Робототехника (2)", callback_data='lesson22')
        lesson23 = types.InlineKeyboardButton(text="Русский язык (9)", callback_data='lesson23')
        lesson24 = types.InlineKeyboardButton(text="Социология (3)", callback_data='lesson24')
        lesson25 = types.InlineKeyboardButton(text="Теория и история музыки (2)", callback_data='lesson25')
        lesson26 = types.InlineKeyboardButton(text="Физика (23)", callback_data='lesson26')
        lesson27 = types.InlineKeyboardButton(text="Филология (7)", callback_data='lesson27')
        lesson28 = types.InlineKeyboardButton(text="Философия (2)", callback_data='lesson28')
        lesson29 = types.InlineKeyboardButton(text="Финансовая грамотность (5)", callback_data='lesson29')
        lesson30 = types.InlineKeyboardButton(text="Химия (16)", callback_data='lesson30')
        lesson31 = types.InlineKeyboardButton(text="Экология (2)", callback_data='lesson31')
        lesson32 = types.InlineKeyboardButton(text="Экономика (9)", callback_data='lesson32')

        keyboard.add(
            lesson1, lesson2, lesson3, lesson4, lesson5, lesson6, lesson7, lesson8, lesson9, lesson10, lesson11,
            lesson12, lesson13, lesson14, lesson15, lesson16, lesson17, lesson18, lesson19, lesson20, lesson21,
            lesson22, lesson23, lesson24, lesson25, lesson26, lesson27, lesson28, lesson29, lesson30, lesson31,
            lesson32)

        global olympiad_name
        olympiad_name = olympiad_dict[message.text][0]
        bot.send_message(message.chat.id, f'📌Выбери предмет, по которому пишешь {olympiad_name}', reply_markup=keyboard)

    def pick_participation_stage(message):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        passed_registration = types.InlineKeyboardButton(text="✏️Прошёл регистрацию",
                                                         callback_data='passed_registration')
        wrote_qualifying = types.InlineKeyboardButton(text="📝Написал отборочный этап", callback_data='wrote_qualifying')
        passed_final = types.InlineKeyboardButton(text="🔝Прошёл на заключительный этап", callback_data='passed_final')
        took_final = types.InlineKeyboardButton(text="🏅Принял участие в финале(участник)", callback_data='took_final')
        final_prize_winner = types.InlineKeyboardButton(text="🥈🥉Призёр финала(диплом 2 или 3 степени)",
                                                        callback_data='final_prize_winner')
        winner_of_final = types.InlineKeyboardButton(text="🥇Победитель финала(диплом 1 степени)",
                                                     callback_data='winner_of_final')

        keyboard.add(passed_registration, wrote_qualifying, passed_final, took_final, final_prize_winner,
                     winner_of_final)

        global olympiad_name
        bot.send_message(message.chat.id,
                         "☑️Вы выбрали олимпиаду: " + olympiad_name +
                         '\n 📚Укажите этап участия в олимпиаде в данный момент', reply_markup=keyboard)

    def pick_mentor(message):
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        mentor1 = types.InlineKeyboardButton(text="👨‍🏫Насртдинов Алмаз Касимович", callback_data='mentor1')
        mentor2 = types.InlineKeyboardButton(text="👨‍🏫Казнабаев Ильдар Гильфанович", callback_data='mentor2')
        mentor3 = types.InlineKeyboardButton(text="👩‍🏫Латыпова Альфия Файзрахмановна", callback_data='mentor3')
        mentor4 = types.InlineKeyboardButton(text="👩‍🏫Гайсина Гузель Фаритовна", callback_data='mentor4')
        mentor5 = types.InlineKeyboardButton(text="👩‍🏫Ахунова Гульнур Юсуповна", callback_data='mentor5')
        mentor6 = types.InlineKeyboardButton(text="👨‍🏫Туктаров Фанзиль Илгамович", callback_data='mentor6')
        mentor7 = types.InlineKeyboardButton(text="👩‍🏫Спевак Мария Владимировна", callback_data='mentor7')
        mentor8 = types.InlineKeyboardButton(text="👩‍🏫Хамидуллина Зульфия Хурматовна", callback_data='mentor8')
        mentor9 = types.InlineKeyboardButton(text="👩‍🏫Бондарева Лилия Егоровна", callback_data='mentor9')
        mentor10 = types.InlineKeyboardButton(text="👩‍🏫Ахметова Гузель Рафкатовна", callback_data='mentor10')
        mentor11 = types.InlineKeyboardButton(text="👩‍🏫Бывшева Алена Сергеевна", callback_data='mentor11')
        mentor12 = types.InlineKeyboardButton(text="👩‍🏫Зайнетдинова Зилфера Арсланбиковна", callback_data='mentor12')
        mentor13 = types.InlineKeyboardButton(text="👩‍🏫Баталлова Лилия Маратовна", callback_data='mentor13')
        mentor14 = types.InlineKeyboardButton(text="👩‍🏫Губайдуллина Рамзия Ишмухаметовна", callback_data='mentor14')

        keyboard.add(mentor1, mentor2, mentor3, mentor4, mentor5, mentor6, mentor7, mentor8, mentor9, mentor10,
                     mentor11, mentor12, mentor13, mentor14)
        bot.send_message(message.chat.id, '📌Выбери своего наставника', reply_markup=keyboard)

    def correct_chak_olymp(message):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        yes_button = types.InlineKeyboardButton(text="Да", callback_data='correct')
        no_button = types.InlineKeyboardButton(text="Нет", callback_data='not_correct')
        keyboard.add(yes_button, no_button)

        global name_user
        global olympiad_name
        global lesson
        global part_stage
        global mentor
        bot.send_message(message.chat.id,
                         f'👦Имя: , {name_user}\n'
                         f'🏆Олимпиада: {olympiad_name}\n'
                         f'📚Предмет: {lesson}\n'
                         f'📎Этап: {part_stage}\n'
                         f"📌Наставник: {mentor}", reply_markup=keyboard)

    def new_olymp_reg():
        global name_user
        global olympiad_name
        global lesson
        global part_stage
        global mentor
        cursor_olymp.execute('INSERT INTO olympiad VALUES (?, ?, ?, ?, ?)',
                             (name_user, olympiad_name, lesson, part_stage, mentor))
        db_olympiad.commit()

    def user_olympiad_list(message):
        user_name = receive_user_name(message)
        cursor_olymp.execute("SELECT * FROM olympiad")
        massive_big = cursor_olymp.fetchall()
        user_olympiad_string = '<b>📄Список ваших олимпиад:</b>\n\n'
        for i in range(len(massive_big)):
            if massive_big[i][0] == user_name:
                user_olympiad_string += f'<b>🎯Олимпиада:</b> {massive_big[i][1]}' \
                                        f'<b>Предмет:</b> {massive_big[i][2]}\n' \
                                        f'<b>Этап:</b> {massive_big[i][3]}\n' \
                                        f'<b>Наставник:</b> {massive_big[i][4]}\n\n'

        bot.send_message(message.chat.id, user_olympiad_string, parse_mode="HTML")
        button_message(message)

    def my_rating_place(message):
        user_name = receive_user_name(message)
        cursor_olymp.execute("SELECT * FROM olympiad")
        massive_big = cursor_olymp.fetchall()
        

    @bot.callback_query_handler(func=lambda call: True)
    def answer(call):
        cursor.execute(f"SELECT olympiad_index FROM user WHERE chat_id = '{call.message.chat.id}'")
        olympiad_index = int(cursor.fetchone()[0])

        if call.data == 'next_15':
            bot.delete_message(call.message.chat.id, call.message.id)
            olympiad_index += 1
            cursor.execute(
                f"UPDATE user set olympiad_index = '{olympiad_index}' WHERE chat_id = '{call.message.chat.id}'")
            send_olympiad_list(call.message, olympiad_index)

        elif call.data == 'past_15':
            bot.delete_message(call.message.chat.id, call.message.id)
            olympiad_index -= 1
            cursor.execute(
                f"UPDATE user set olympiad_index = '{olympiad_index}' WHERE chat_id = '{call.message.chat.id}'")
            send_olympiad_list(call.message, olympiad_index)

        elif call.data == 'pick_olympiad':
            msg = bot.send_message(call.message.chat.id, '📋Выбери номер нужной тебе олимпиады')
            bot.register_next_step_handler(msg, pick_olymp)

        elif 'lesson' in call.data:
            global lesson
            lesson = lessons_dict[call.data]
            bot.delete_message(call.message.chat.id, call.message.id)
            pick_participation_stage(call.message)

        elif call.data in (
                'passed_registration', 'wrote_qualifying', 'passed_final', 'took_final', 'final_prize_winner',
                'winner_of_final'):
            global part_stage
            part_stage = participation_stage_dict[call.data]
            bot.delete_message(call.message.chat.id, call.message.id)
            pick_mentor(call.message)

        elif 'mentor' in call.data:
            global mentor
            mentor = mentors_dict[call.data]
            bot.delete_message(call.message.chat.id, call.message.id)
            # try:
            correct_chak_olymp(call.message)
            # except Exception as e:
            # bot.send_message(call.message.chat.id, f'Произошла ошибка {e}')

        elif call.data in ('correct', 'not_correct'):
            if call.data == 'correct':
                try:
                    new_olymp_reg()
                    bot.delete_message(call.message.chat.id, call.message.id)
                    bot.send_message(call.message.chat.id, 'Вы успешно зарегистрировали олимпиаду')
                    button_message(call.message)
                except EOFError:
                    bot.send_message(call.message.chat.id, f'При регистрации олимпиады произошла ошибка {e}')

    @bot.message_handler(content_types=['text'])
    def button_answer(message):
        text = message.text

        cursor.execute(f"SELECT chat_id FROM user WHERE chat_id = '{message.chat.id}'")
        if cursor.fetchone() is None:
            if len(message.text.split()) == 3:
                name(message)
        elif text == '✏️Зарегистрироваться на олимпиаду':
            send_olympiad_list(message, 0)
        elif text == '📄Мои олимпиады':
            user_olympiad_list(message)
        elif text == '🏆Моё место в рейтинге':
            my_rating_place(message)
        elif text == '🔃Поменять имя':
            pass
        elif text == '📊Статистика олимпиад':
            pass
    bot.polling()


if __name__ == '__main__':
    main()
