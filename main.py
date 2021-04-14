"""
Этот код является кодом ботом для любого сообщества вк.
В данной части документации будут описаны основные функции и методы работы с
ботом основные
Большая часть этого года написано vk.com/x_vl_x поэтоуму по всем вопросом обращаться к нему
В коментариях могут быть граматические ошибки, потомучто я безграмотный)))
"""

import calendar  # https://docs.python.org/3/library/calendar.html
import json  # https://docs.python.org/3/library/json.html?highlight=json#module-json
import vk_api  # https://pypi.org/project/vk-api/
from vk_api.longpoll import VkLongPoll, VkEventType  # https://vk-api.readthedocs.io/en/latest/longpoll.html
from datetime import *  # https://pypi.org/project/vk-api/
from config import main_token
from parcer import *
import sqlite3 as sqlite

"""
В файле config хранится строка main_token в которой прописан ключ
доступа к API группы

В parcer.py находятся отдельные функции, для парсинга ecampus
"""

vk_session = vk_api.VkApi(token=main_token)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

""" Подключение к вк сессии"""

"""
Ниже представлены все символьные константы, используемы в програме
"""

UP_DAY = 'Monday'  # День в который бот обновляет распиание(день недели на английском языке)

DAYS = {
    'Monday': 'Понедельник',
    'Tuesday': 'Вторник',
    'Wednesday': 'Среда',
    'Thursday': 'Четверг',
    'Friday': 'Пятница',
    'Saturday': 'Суббота ',
    'Sunday': 'Воскресенье'
}

DAY_OF_WEEK = {
    'Понедельник',
    'Вторник',
    'Среда',
    'Четверг',
    'Пятница',
    'Суббота ',
    'Воскресенье'
}

CHO0SE_ACTION = 'Выберите действие'
CHO0SE_GROUP = 'Выберите вашу подгруппу'
MAILING_MSG = 'Введите текст, который будет разослан ❗ВСЕМ❗ пользователям'
MAILING_COM_MSG = 'Вам пришло сообщение с рассылки:'
MAILING_ADM_MSG = 'Рассылка выполнена со следующим текстом:'
MSG_FOR_MAILING = 'Сообщение для рассылки'
DEV_MSG = "Над этим проектом работали:\n" \
          "vk.com/x_vl_x\n" \
          "vk.com/mishadukhno\n"

WARNING_MSG = '❗Внимание❗\n' \
              'Будьте пределно внимательны при использовании данной функции\nРассылка производистя всем пользователям' \
              ' данного бота\n❗Внимание❗\n'

"""
Статусы пользователей
"""

STATUS_ADM = 'admin'
STATUS_COM = 'common'

"""
mode пользователя или та вкладка на которой он находится
"""

MODE_0 = 'start'
MODE_1 = 'a_start'
MODE_2 = 'rasp'
MODE_3 = 'dev'
MODE_4 = 'a_send'
MODE_5 = 'first_group'
MODE_6 = 'second_group'
MODE_7 = 'in_adm_panel'
MODE_8 = 'check_send'
MODE_9 = 'schedule_1'
MODE_10 = 'schedule_2'

"""Список сообщений, которыыми можно запустить бота"""

START_MSG = ['начать', '/start', 'start', '/начать']

"""Ниже обьявленые все 3, на текущий момент класса, которые есть в программе"""


class Attachments:  # Класс в хранящий в себе все вложения с личного сообщения

    def __init__(self, attachment_type, owner_id, doc_id, access_key):
        self.attachment_type = attachment_type  # Тип вложения
        self.owner_id = owner_id  # Тот, кто отправил вложение первоночально
        self.doc_id = doc_id  # ID вложения
        self.access_key = access_key  # Ключ доступа ко вложению

    """
    Подробнее: https://vk.com/dev/messages.send
    Функция make_attachment создает строку attachment, как в примере по ссылке выше
    """

    def make_attachment(self):
        if self.access_key is not None:
            return str(self.attachment_type) + str(self.owner_id) + '_' + str(self.doc_id) + '_' + str(self.access_key)
        else:
            return str(self.attachment_type) + str(self.owner_id) + '_' + str(self.doc_id)


class User:  # Класс пользователя

    def __init__(self, id, status, mode):
        self.id = id  # ID вкнотакте пользователя
        self.status = status  # Статус пользователя admin/common
        self.mode = mode  # Текущая вкладка в которой находится пользователь


class Today_Schedule:  # Расписание на сегодня, содержит данные с ecampus

    def __init__(self, teacher, lesson, time_start, time_end, aud, podgroup, number, lessontype, wek_day):
        self.teacher = teacher
        self.lesson = lesson
        self.time_start = time_start
        self.time_end = time_end
        self.aud = aud
        self.podgroup = podgroup
        self.number = number
        self.lessontype = lessontype
        self.wek_day = wek_day


# -------------------------Следующие функции используются для работы с базой данных date_base.db--------------------------------

conn = None
cur = None  # Курсор для отправки запросов к бд
try:
    conn = sqlite.connect("date_base.db")  # Здесь создаётся или если уже создан, то открывается файл базы данных
    cur = conn.cursor()
except Exception as e:
    print("Ошибка подключения к бд:")  # Сообщение ошибки в случае некорректного подключения
    print(e)


def dataBaseTables(cur,
                   conn):  # Данная функция создаёт таблицы с именами users и teachers в базе данных, если они не созданы
    try:
        # query - Переменная в которой хранится sql запрос к базе данных
        cur.execute("""CREATE TABLE IF NOT EXISTS users(
            userid INT PRIMARY KEY,
            user_status TEXT,
            user_screen TEXT);""")  # Отправка запроса к базе данных
        cur.execute("""CREATE TABLE IF NOT EXISTS teachers(
            teacherid INT PRIMARY KEY,
            teacher_name TEXT,
            teacher_href TEXT);""")  # Отправка запроса к базе данных
        conn.commit()  # Сохранение изменений внесённых в бд
    except Exception as e:
        print(
            "Не удалось отправить запрос по созданию таблиц:")  # Сообщение ошибки в случае некорректной работы запросов
        print(e)


def dataBaseCompletionUsers(id, status, mode, cur,
                            conn):  # Эта функция заполняет таблицу users базы данных data_base.db данными подаваемыми на вход
    # Добавление пользователя в БД
    try:
        query = "INSERT INTO users(userid, user_status, user_screen) VALUES( '{0}', '{1}', '{2}');".format(id, status,
                                                                                                           mode)  # Составление запроса
        cur.execute(query)  # Отправка запроса к базе данных
        conn.commit()  # Сохранение изменений внесённых в бд
    except Exception as e:
        print("Ошибка внесения данных в таблицу users:")  # Сообщение ошибки в случае некорректной работы запросов
        print(e)


def dataBaseGetTeachers(teacher_name, cur, conn):
    try:
        query = """SELECT teacher_href FROM teachers
                    WHERE
                    teacher_name = '{0}'""".format(teacher_name)  # Запрос на выборку ссылки на преподавателя по имени
        cur.execute(query)  # Выполнение запроса
        selection = cur.fetchone()  # Получение результата запроса(Выборка)
        conn.commit()  # Сохранение изменений внесённых в бд
        if selection is None:
            temp_bd_parc = "Упс..., у меня её нет"
        else:
            temp_bd_parc = selection[0]
        return temp_bd_parc
    except Exception as e:
        print("Ошибка запроса к базе данных:")
        print(e)


def dataBaseGetUsers(cur, conn):
    try:
        query = """ SELECT * FROM users"""  # Запрос на выборку всех пользователей
        cur.execute(query)  # Выполнение запроса
        selection = cur.fetchall()  # Получение результата запроса(Выборка)
        conn.commit()  # Сохранение изменений внесённых в бд
        return selection
    except Exception as e:
        print("Ошибка выборки пользователей:")
        print(e)


def dataBaseUpdateUsers(id, status, mode, cur, conn):
    # Эта функция заполняет таблицу users базы данных data_base.db данными подаваемыми на вход
    # Добавление пользователя в БД
    try:
        query = "UPDATE users SET user_screen = '{0}' WHERE userid = {1}".format(mode, id)  # Составление запроса
        cur.execute(query)  # Отправка запроса к базе данных
        conn.commit()  # Сохранение изменений внесённых в бд
    except Exception as e:
        print("Ошибка внесения изменений в таблицу users:")  # Сообщение ошибки в случае некорректной работы запросов
        print(e)


dataBaseTables(cur, conn)
# --------------------------------------------------На этом функции работы с базой данных
# заканчиваются-------------------------------------


# file = "date_base.txt"
"""
Нижи идет заполнение массива users пользователями из бд
users - обект класса User
"""
us = dataBaseGetUsers(cur, conn)

users = []
for line in us:
    users.append(User(int(line[0]), line[1], line[2]))


def schendule(status, cur, conn):
    """
    Данная функция возвращает 4 разные строки, в зависимости от status
    :param status: принимает 4 значения
    1 - возвращает расписание на сегодня для первой подгруппы
    2 - возвращает расписание на сегодня для второй подгруппы
    3 - возвращает расписание на неделю для первой подгруппы
    4 - возвращает расписание на неделю для второй подгруппы
    """
    cur_time = event.datetime + timedelta(hours=3)  # считает текущее время по Москве
    weekday = calendar.day_name[cur_time.weekday()]  # считает текущий день недели
    schedule_message_1 = ''
    schedule_message_2 = ''
    week_schedule_message_1 = ''
    week_schedule_message_2 = ''
    cur_day = ''
    for para in week_lessons:
        try:
            if para.wek_day != cur_day:
                week_schedule_message_1 += para.wek_day + ':\n\n'
                week_schedule_message_2 += para.wek_day + ':\n\n'
                cur_day = para.wek_day

            if para.podgroup == '(1)':
                week_schedule_message_1 += get_schedule_message(para, cur, conn)

            elif para.podgroup == '(2)':
                week_schedule_message_2 += get_schedule_message(para, cur, conn)

            elif para.podgroup == '(1, 2)' or para.podgroup == '':
                week_schedule_message_2 += get_schedule_message(para, cur, conn)
                week_schedule_message_1 += get_schedule_message(para, cur, conn)
        except Exception:
            pass

        if DAYS.get(weekday) == para.wek_day:
            if para.podgroup == '(1)':
                schedule_message_1 += get_schedule_message(para, cur, conn)

            elif para.podgroup == '(2)':
                schedule_message_2 += get_schedule_message(para, cur, conn)

            elif para.podgroup == '(1, 2)' or para.podgroup == '':
                schedule_message_2 += get_schedule_message(para, cur, conn)
                schedule_message_1 += get_schedule_message(para, cur, conn)

    schedule_message_2 = schedule_message_check(schedule_message_2)
    schedule_message_1 = schedule_message_check(schedule_message_1)

    if status == 1:
        return schedule_message_1
    if status == 2:
        return schedule_message_2
    if status == 3:
        return week_schedule_message_1
    if status == 4:
        return week_schedule_message_2


def schedule_message_check(schedule_message):
    """
    :param schedule_message: сообщение расписания
    :return: проверяет пустое расписание на сегодня или нет и возвращает отредактированное сообщение
    """
    result = ""
    if len(schedule_message) == 0:
        result = 'Сегодня пар нет' + schedule_message
    else:
        result = 'Расписание на сегодня:\n\n' + schedule_message

    return result


def get_schedule_message(para, cur, conn):
    """
    :param para: обект типа Today_Schedule
    :return: сообщение с выводом того, что хранится в para
    """
    result = ''
    result += 'Номер пары: ' + str(para.number) + '\n'
    result += 'С: ' + str(para.time_start.strftime('%H:%M')) + ' до: ' + \
              str(para.time_end.strftime('%H:%M')) + '\n'
    result += str(para.lesson) + '\n'
    result += 'Аудитория: ' + str(para.aud) + '\n'
    result += 'Тип пары: ' + str(para.lessontype) + '\n'
    result += 'Препод: ' + str(para.teacher) + '\n'
    result += 'Ссылка БББ: ' + dataBaseGetTeachers(str(para.teacher), cur, conn)
    result += '\n\n'
    return result


def get_keyboard(state, buts):  # функция создания клавиатур я ее спер с видоса
    """
    :param state:
    False - кнопка будет в формате клавиатуры
    True - инлайн кнопка
    https://vk.com/dev/bots_docs_3
    """
    nb = []
    for iterator in range(len(buts)):
        nb.append([])
        for k in range(len(buts[iterator])):
            nb[iterator].append(None)
    for iterator in range(len(buts)):
        for k in range(len(buts[iterator])):
            text = buts[iterator][k][0]
            color = {'green': 'positive', 'red': 'negative', 'blue': 'primary', 'white': 'secondary'}[
                buts[iterator][k][1]]
            nb[iterator][k] = {
                "action": {"type": "text", "payload": "{\"button\": \"" + "1" + "\"}", "label": f"{text}"},
                "color": f"{color}"}
    first_keyboard = {'one_time': False, 'buttons': nb, 'inline': state}
    first_keyboard = json.dumps(first_keyboard, ensure_ascii=False).encode('utf-8')
    first_keyboard = str(first_keyboard.decode('utf-8'))
    return first_keyboard


def sender(id, text, key, attachment):
    """
    :param id: Польхователь которму отправят сообщение
    :param text: текст сообщения
    :param key: клавиутура с кнопками
    :param attachment: вложение сообщения
    """
    vk_session.method('messages.send',
                      {'user_id': id,
                       'message': text,
                       'random_id': 0,
                       'keyboard': key,
                       'dont_parse_links': 1,
                       'attachment': attachment
                       })


def get_text(msg):  # Функция преобразования пересланых сообщений в массив строк
    """
    :param msg: сообщение
    :return: функция не универсальна поэтому весь текст будет хранится в переменной ans_txt_msg
    """
    try:
        if msg is not None:
            for i in msg:
                if i.get('text') != '':
                    ans_txt_msg.append(i.get('text'))
                get_text(i.get('fwd_messages'))
    except Exception:
        print('Произошла ошибка в функции get_text')


def get_attachments(item):  # Функция преобразования пересланых сообщений в массив строк
    """
    :param item: сообщение
    :return: функция не универсальна поэтому весь текст будет хранится в переменной ans_attach
    """
    try:
        if item is not None:
            for i in item:
                if len(i.get('attachments')) != 0:
                    ans_attach.append(i.get('attachments'))
                get_attachments(i.get('fwd_messages'))
    except Exception:
        print('Произошла ошибка в функции get_attachments')


def change_mode(id, cur, conn):
    """
    Перезаписывает текущее состояние пользователей в БД
    """
    global users
    for user in users:
        if user.id == id:
            dataBaseUpdateUsers(user.id, user.status, user.mode, cur, conn)


"""
Описание клавиатур
"""
start_key = get_keyboard(False, [  # Стартовая клавиаутра пользователя со статусом common
    [('расписание', 'green'), ('разработчики', 'white')]
])

adm_start_key = get_keyboard(False, [  # Стартовая клавиаутра пользователя со статусом admin
    [('рассылка', 'red'), ('расписание', 'green'), ('разработчики', 'white')]
])

back_key = get_keyboard(False, [  # Клавиша назад
    [('назад', 'blue')]
])

adm_panel_key = get_keyboard(False, [  # Кнопка подтверждения во время отправки соощений в рассылку
    [('нет', 'red'), ('да', 'green')]
])

in_schedule_key = get_keyboard(False, [  # Кнопка выбора внутри расписания
    [('первая подгруппа', 'green'), ('вторая подгруппа', 'green')],
    [('назад', 'blue')]
])

ready_send = get_keyboard(False, [  # Кнопки внутри рассылки
    [('назад', 'blue'), ('ввести текст для рассылки', 'green')]
])

group_key = get_keyboard(False, [  # Кнопки выбора дня недели
    [('расписание на сегодня', 'green'), ('расписание на неделю', 'green')],
    [('назад', 'blue')]
])

empty_key = get_keyboard(False, [])  # Пустая кнопка

s = ''
final_attachment = ''
flag = True  # флаг проверки обновления расписания в UP_DAY
first_start = True  # флаг проверки первого запуска бота
week_lessons = []  # массив пар на текущуу неделю

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            id = event.user_id  # Получаем VK ID отправителя сообщения боту
            msg = event.text.lower()  # Переводим текст сообщения в нижний регистр
            time = event.datetime + timedelta(hours=3)
            update_day = calendar.day_name[time.weekday()]  # update_day харнит текущий день
            if (update_day == UP_DAY and flag) or first_start:  # если update_day это день в который мы обновляем бота
                # или бот запушен первый раз, то мы обновляем расписание на неделю
                flag = False
                first_start = False
                week_lessons = []
                schedule = get_schedule()  # schedule хранит словарь со всеми днями недели
                if schedule is not None:  # расписание на неделю не пустое
                    for item_day in schedule:  # перебор всех дней недели с парами
                        for day in DAY_OF_WEEK:  # Перебор всех дней недели на русском
                            if get_today_schedule(day, item_day):  # Проверка на то, есть сегодня пары или нет
                                # print(day)
                                today = item_day.get('Lessons')
                                for i in today:  # добавление всех сегодняшних пар в массив week_lessons
                                    week_lessons.append(Today_Schedule(
                                        teacher=i.get('Teacher').get('Name'),
                                        lesson=i.get('Discipline'),
                                        time_start=datetime.strptime(i.get('TimeBegin'), "%Y-%m-%d %H:%M:%S"),
                                        time_end=datetime.strptime(i.get('TimeEnd'), "%Y-%m-%d %H:%M:%S"),
                                        aud=i.get('Aud').get('Name'),
                                        podgroup=i.get('Groups')[0].get('Subgroup'),
                                        number=i.get('PairNumberStart'),
                                        lessontype=i.get('LessonType'),
                                        wek_day=day
                                    ))

            elif update_day != UP_DAY:
                flag = True  # Сброс flag, чтобы обновить все в следеющий UP_DAY

            if msg in START_MSG:
                flag1 = True
                # True - если юзера нет в БД
                # False - если он есть в БД
                for user in users:
                    print(user.status)
                    if user.id == id:

                        if user.status == STATUS_ADM:
                            user.mode = MODE_1
                            sender(user.id, CHO0SE_ACTION, adm_start_key, [])
                            # Перевод пользователя на соотвествующий главный экран

                        else:
                            user.mode = MODE_0
                            sender(user.id, CHO0SE_ACTION, start_key, [])
                            # Перевод пользователя на соотвествующий главный экран

                        flag1 = False

                if flag1:
                    # Добавление пользователя в БД
                    dataBaseCompletionUsers(int(id), STATUS_COM, MODE_0, cur, conn)
                    # users.append(User(id, STATUS_COM, MODE_0))
                    # f = open(file, mode='a', encoding='utf-8')
                    # f.write(str(id) + ':' + STATUS_COM + ':' + MODE_0 + '\n')
                    # f.close()
                    # Перевод пользователя на соотвествующий главный экран
                    sender(int(id), CHO0SE_ACTION, start_key, [])

            """
            Далее идет обработка всех команд посылаемых боту
            """

            for user in users:
                if user.id == id:
                    """
                    Сначала идет обработка команд от admin
                    """
                    if user.status == STATUS_ADM:

                        if user.mode == MODE_1:
                            # Если пользователь на главном экране
                            if msg == 'расписание':
                                # Если нажата кнопка расписание
                                user.mode = MODE_2
                                sender(user.id, CHO0SE_GROUP, in_schedule_key, [])

                            elif msg == 'разработчики':
                                # Если нажата кнопка # Если нажата кнопка расписание
                                user.mode = MODE_3
                                sender(user.id, DEV_MSG, back_key, [])
                                sender(user.id, CHO0SE_ACTION, back_key, [])

                            elif msg == 'рассылка':
                                # Если нажата кнопка рассылка
                                user.mode = MODE_4
                                sender(user.id, WARNING_MSG, ready_send, [])

                        elif user.mode == MODE_3:
                            # Если пользователь во вкладке разработчки
                            if msg == 'назад':
                                # Если нажата кнопка назад
                                user.mode = MODE_1
                                sender(user.id, CHO0SE_ACTION, adm_start_key, [])

                        elif user.mode == MODE_2:
                            # Если пользователь во вкладке расписание
                            if msg == 'первая подгруппа':
                                # Если нажата кнопка первая подгруппа
                                user.mode = MODE_5
                                sender(user.id, CHO0SE_ACTION, group_key, [])
                            elif msg == 'вторая подгруппа':
                                # Если нажата кнопка вторая подгруппа
                                user.mode = MODE_6
                                sender(user.id, CHO0SE_ACTION, group_key, [])
                            elif msg == 'назад':
                                # Если нажата кнопка назад
                                user.mode = MODE_1
                                sender(user.id, CHO0SE_ACTION, adm_start_key, [])

                        elif user.mode == MODE_4:
                            # Если пользователь во вкладке рассылка
                            if msg == 'назад':
                                # Если нажата кнопка назад
                                user.mode = MODE_1
                                sender(user.id, CHO0SE_ACTION, adm_start_key, [])

                            elif msg == 'ввести текст для рассылки':
                                # Если нажата кнопка ввести текст для рассылки
                                user.mode = MODE_8
                                sender(user.id, MAILING_MSG, empty_key, [])

                        elif user.mode == MODE_7:
                            # Если введено сообщение для рассылки
                            if msg == 'да':
                                # Если нажата кнопка да, то отправяет сообщение s c вложением final_attachment всем
                                for user_send in users:
                                    if user_send.status == STATUS_ADM:
                                        user_send.mode = MODE_1
                                        sender(user_send.id, MAILING_ADM_MSG, adm_start_key, '')
                                        sender(user_send.id, s, adm_start_key, final_attachment)

                                    elif user_send.status == STATUS_COM:
                                        user_send.mode = MODE_0
                                        sender(user_send.id, s, start_key, final_attachment)
                                    change_mode(user_send.id, cur, conn)

                            elif msg == 'нет':
                                # Если нажата кнопка нет, то переносит на главынй экран
                                user.mode = MODE_1
                                sender(user.id, CHO0SE_ACTION, adm_start_key, [])

                        elif user.mode == MODE_8:
                            # Если пользователь во влкадке ввода текста для рассылки
                            s = ''
                            final_attachment = ""
                            f_msg = vk.messages.getById(message_ids=event.message_id)
                            # f_msg хранит полное сообщение со всеми вложениеями и текстом
                            f_msg = f_msg.get('items')

                            ans_attach = []
                            get_attachments(f_msg)  # Функция get_attachments
                            # Все вложения хранятся в ans_attach
                            our_attachment = []
                            for mas_cur_attach in ans_attach:
                                for cur_attach in mas_cur_attach:
                                    attachment_type = cur_attach.get('type')
                                    content = cur_attach.get(attachment_type)
                                    if str(attachment_type) == 'wall':
                                        our_attachment.append(Attachments(
                                            attachment_type,
                                            content.get('from_id'),
                                            content.get('id'),
                                            content.get('access_key')
                                        ))
                                    else:
                                        our_attachment.append(Attachments(
                                            attachment_type,
                                            content.get('owner_id'),
                                            content.get('id'),
                                            content.get('access_key')
                                        ))
                            # Формируем вложение для отправки
                            for attachment in our_attachment:
                                final_attachment += attachment.make_attachment() + ','
                            final_attachment = final_attachment.strip(',')

                            # Весб текст хранятся в ans_txt_msg

                            f_msg = f_msg[0]
                            ans_txt_msg = []
                            if f_msg.get('text') != '':
                                ans_txt_msg.append(f_msg.get('text'))

                            get_text(f_msg.get('fwd_messages'))

                            # Формируем текст для отправки

                            for txt in ans_txt_msg:
                                s += txt
                                s += '\n'
                            user.mode = MODE_7
                            sender(user.id, MSG_FOR_MAILING, adm_panel_key, '')
                            sender(user.id, s, adm_panel_key, final_attachment)

                        elif user.mode == MODE_5 or user.mode == MODE_6:
                            # Если пользователь во вкладке первая или вторая подгруппа
                            if user.mode == MODE_5:
                                # Если пользователь во вкладке первая подгруппа
                                if msg == 'расписание на сегодня':
                                    # Если пользователь нажал на кнопку расписание на сегодня
                                    user.mode = MODE_9
                                    sender(user.id, schendule(1, cur, conn), back_key, [])
                                if msg == 'расписание на неделю':
                                    # Если пользователь нажал на кнопку расписание на неделю
                                    user.mode = MODE_9
                                    sender(user.id, schendule(3, cur, conn), back_key, [])
                            if user.mode == MODE_6:
                                # Если пользователь во вкладке вторая подгруппа
                                if msg == 'расписание на сегодня':
                                    # Если пользователь нажал на кнопку расписание на сегодня
                                    user.mode = MODE_10
                                    sender(user.id, schendule(2, cur, conn), back_key, [])
                                if msg == 'расписание на неделю':
                                    # Если пользователь нажал на кнопку расписание на неделю
                                    user.mode = MODE_10
                                    sender(user.id, schendule(4, cur, conn), back_key, [])
                            if msg == 'назад':
                                # Если пользователь нажал на кнопку назад
                                user.mode = MODE_2
                                sender(user.id, CHO0SE_GROUP, in_schedule_key, [])

                        elif user.mode == MODE_9:
                            # Если пользователь во вкладке расписания первой подгруппы
                            if msg == 'назад':
                                user.mode = MODE_5
                                sender(user.id, CHO0SE_ACTION, group_key, [])
                        elif user.mode == MODE_10:
                            # Если пользователь во вкладке расписания первой подгруппы
                            if msg == 'назад':
                                user.mode = MODE_6
                                sender(user.id, CHO0SE_ACTION, group_key, [])

                    elif user.status == STATUS_COM:
                        # Если статус пользоватея common
                        # Вся обработка выполняется аналогично, как для статуса admin, но с отсусутвием функциий админа
                        if user.mode == MODE_0:

                            if msg == 'расписание':
                                user.mode = MODE_2
                                sender(user.id, CHO0SE_GROUP, in_schedule_key, [])

                            elif msg == 'разработчики':
                                user.mode = MODE_3
                                sender(user.id, DEV_MSG, back_key, [])
                                sender(user.id, CHO0SE_ACTION, back_key, [])

                        elif user.mode == MODE_3:

                            if msg == 'назад':
                                user.mode = MODE_0
                                sender(user.id, CHO0SE_ACTION, start_key, [])

                        elif user.mode == MODE_2:
                            if msg == 'первая подгруппа':
                                user.mode = MODE_5
                                sender(user.id, CHO0SE_ACTION, group_key, [])

                            elif msg == 'вторая подгруппа':
                                user.mode = MODE_6
                                sender(user.id, CHO0SE_ACTION, group_key, [])

                            elif msg == 'назад':
                                user.mode = MODE_0
                                sender(user.id, CHO0SE_ACTION, start_key, [])

                        elif user.mode == MODE_5 or user.mode == MODE_6:

                            if user.mode == MODE_5:

                                if msg == 'расписание на сегодня':
                                    user.mode = MODE_9
                                    sender(user.id, schendule(1, cur, conn), back_key, [])

                                if msg == 'расписание на неделю':
                                    user.mode = MODE_9
                                    sender(user.id, schendule(3, cur, conn), back_key, [])

                            if user.mode == MODE_6:

                                if msg == 'расписание на сегодня':
                                    user.mode = MODE_10
                                    sender(user.id, schendule(2, cur, conn), back_key, [])

                                if msg == 'расписание на неделю':
                                    user.mode = MODE_10
                                    sender(user.id, schendule(4, cur, conn), back_key, [])

                            if msg == 'назад':
                                user.mode = MODE_2
                                sender(user.id, CHO0SE_GROUP, in_schedule_key, [])

                        elif user.mode == MODE_9:

                            if msg == 'назад':
                                user.mode = MODE_5
                                sender(user.id, CHO0SE_ACTION, group_key, [])

                        elif user.mode == MODE_10:

                            if msg == 'назад':
                                user.mode = MODE_6
                                sender(user.id, CHO0SE_ACTION, group_key, [])

            change_mode(id, cur, conn)
