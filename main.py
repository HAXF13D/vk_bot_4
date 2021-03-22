import calendar
import json
import vk_api
from parcer import *
from vk_api.longpoll import VkLongPoll, VkEventType
from datetime import *
from config import main_token

vk_session = vk_api.VkApi(token=main_token)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


class User():

    def __init__(self, id, status, mode, group):
        self.id = id
        self.status = status
        self.mode = mode
        self.group = group


class Today_Schedule():

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


class Week_Schedule():

    def __init__(self, monday, tuesday, wednesday, thursday, friday, saturday, sunday):
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday


file = "date_base.txt"

f = open(file, mode='r', encoding='utf-8')
users = []
for line in f:
    line = line.split(':')
    if (line != ''):
        users.append(User(line[0], line[1], line[2], line[3]))
f.close()


def get_keyboard(state, buts):  # функция создания клавиатур
    nb = []
    color = ''
    for i in range(len(buts)):
        nb.append([])
        for k in range(len(buts[i])):
            nb[i].append(None)
    for i in range(len(buts)):
        for k in range(len(buts[i])):
            text = buts[i][k][0]
            color = {'green': 'positive', 'red': 'negative', 'blue': 'primary', 'white': 'secondary'}[
                buts[i][k][1]]
            nb[i][k] = {"action": {"type": "text", "payload": "{\"button\": \"" + "1" + "\"}", "label": f"{text}"},
                        "color": f"{color}"}
    first_keyboard = {'one_time': False, 'buttons': nb, 'inline': state}
    first_keyboard = json.dumps(first_keyboard, ensure_ascii=False).encode('utf-8')
    first_keyboard = str(first_keyboard.decode('utf-8'))
    return first_keyboard


def sender(id, text, key):
    vk_session.method('messages.send',
                      {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': key, 'dont_parse_links': 1})


def get_text(msg):  # Функция преобразования пересланых сообщений в массив строк
    try:
        if msg is not None:
            for i in msg:
                # print(i.get('text'))
                if i.get('text') != '':
                    ans_txt_msg.append(i.get('text'))
                get_text(i.get('fwd_messages'))
    except Exception:
        print('Произошла ошибка в функции get_text')


def change_mode():
    f = open(file, mode='w', encoding='utf-8')
    for user in users:
        f.write(f"{user.id}:{user.status}:{user.mode}:\n")
    f.close()


start_key = get_keyboard(False, [
    [('расписание', 'green'), ('разработчики', 'white')]
])

adm_start_key = get_keyboard(False, [
    [('рассылка', 'red'), ('расписание', 'green'), ('разработчики', 'white')]
])

back_key = get_keyboard(False, [
    [('назад', 'blue')]
])

adm_panel_key = get_keyboard(False, [
    [('нет', 'red'), ('да', 'green')]
])

in_schedule_key = get_keyboard(False, [
    [('первая подгруппа', 'green'), ('вторая подгруппа', 'green')],
    [('назад', 'blue')]
])

ready_send = get_keyboard(False, [
    [('назад', 'blue'), ('ввести текст для рассылки', 'green')]
])

empty_key = get_keyboard(False, [])

s = ''

flag = False

week_lessons = []

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:

            id = event.user_id
            msg = event.text.lower()
            time = event.datetime + timedelta(hours=3)
            update_day = calendar.day_name[time.weekday()]
            if update_day == 'Tuesday' and flag == False:
                flag = True
                schedule = get_schedule()

                day_of_week = {'Понедельник',
                               'Вторник',
                               'Среда',
                               'Четверг',
                               'Пятница',
                               'Суббота ',
                               'Воскресенье'
                               }
                if schedule is not None:
                    for item_day in schedule:
                        for day in day_of_week:
                            if get_today_schedule(day, item_day) == 1:
                                # print(day)
                                today = item_day.get('Lessons')
                                for i in today:
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

                                    """
                                    print(i.get('Discipline'))
                                    print(i.get('TimeBegin'))
                                    print(i.get('TimeEnd'))
                                    print(i.get('Aud').get('Name'))
                                    print(i.get('LessonType'))
                                    print(i.get('PairNumberStart'))
                                    print(i.get('Teacher').get('Name'))
                                    print(i.get('Groups')[0].get('Subgroup'))
                                    print('\n')
    
                    print(week_lessons[0].wek_day)
                    """

            if msg == 'начать' or msg == '/start' or msg == 'start' or msg == '/начать':
                flag1 = 0
                for user in users:
                    if user.id == str(id):
                        if user.status == 'admin':
                            sender(id, 'Выберите действие', adm_start_key)
                            user.mode = 'a_start'
                        else:
                            sender(id, 'Выберите действие', start_key)
                            user.mode = 'start'
                        flag1 = 1
                if flag1 == 0:
                    users.append(User(id, 'common', 'start', None))
                    print(user.id, " ", user.status)
                    f = open(file, mode='a', encoding='utf-8')
                    f.write(str(id) + ':common:start:None' + '\n')
                    f.close()

                    sender(int(id), 'Выберите действие', start_key)

            for user in users:
                if user.id == str(id):

                    if user.status == 'admin':

                        if user.mode == 'a_start':
                            if msg == 'расписание':

                                user.mode = 'rasp'
                                sender(id, 'Выберите вашу подгруппу', in_schedule_key)

                            elif msg == 'разработчики':

                                user.mode = 'dev'
                                sender(id, 'Над этим проектом работали:\n'
                                           'vk.com/x_vl_x\n'
                                           'vk.com/mishadukhno\n', empty_key)
                                sender(id, 'Выберите действие', back_key)

                            elif msg == 'рассылка':

                                user.mode = 'a_send'
                                sender(id, '❗Внимание❗\n'
                                           'Будьте пределно внимательны при использовании данной функции\n'
                                           'Рассылка производистя всем пользователям данного бота\n'
                                           '❗Внимание❗\n', ready_send)

                        elif user.mode == 'dev':

                            if msg == 'назад':
                                sender(id, 'Выберите действие', adm_start_key)
                                user.mode = 'a_start'

                        elif user.mode == 'rasp':

                            cur_time = event.datetime + timedelta(hours=3)  # считает текущее время мск + 4
                            weekday = calendar.day_name[cur_time.weekday()]  # считает текущий день недели
                            # print(cur_time)
                            days = {'Monday': 'Понедельник',
                                    'Tuesday': 'Вторник',
                                    'Wednesday': 'Среда',
                                    'Thursday': 'Четверг',
                                    'Friday': 'Пятница',
                                    'Saturday': 'Суббота ',
                                    'Sunday': 'Воскресенье'
                                    }

                            # print(days.get(weekday)) #Перевод названия дня недели на русский
                            schedule_message_1 = ''
                            schedule_message_2 = ''
                            for para in week_lessons:
                                # print(para.wek_day)
                                if days.get(weekday) == para.wek_day:
                                    if para.podgroup == '(1)':

                                        schedule_message_1 += 'Номер пары: ' + str(para.number) + '\n'
                                        schedule_message_1 += 'С: ' + str(para.time_start.strftime('%H:%M')) + ' до: ' + \
                                                              str(para.time_end.strftime('%H:%M')) + '\n'
                                        schedule_message_1 += str(para.lesson) + '\n'
                                        schedule_message_1 += 'Аудитория: ' + str(para.aud) + '\n'
                                        schedule_message_1 += 'Тип пары: ' + str(para.lessontype) + '\n'
                                        schedule_message_1 += 'Препод: ' + str(para.teacher) + '\n'
                                        schedule_message_1 += '\n\n'

                                    elif para.podgroup == '(2)':

                                        schedule_message_2 += 'Номер пары: ' + str(para.number) + '\n'
                                        schedule_message_2 += 'С: ' + str(
                                            para.time_start.strftime('%H:%M')) + ' до: ' + \
                                                              str(para.time_end.strftime('%H:%M')) + '\n'
                                        schedule_message_2 += str(para.lesson) + '\n'
                                        schedule_message_2 += 'Аудитория: ' + str(para.aud) + '\n'
                                        schedule_message_2 += 'Тип пары: ' + str(para.lessontype) + '\n'
                                        schedule_message_2 += 'Препод: ' + str(para.teacher) + '\n'
                                        schedule_message_2 += '\n\n'

                                    elif para.podgroup == '(1, 2)' or para.podgroup == '':

                                        schedule_message_2 += 'Номер пары: ' + str(para.number) + '\n'
                                        schedule_message_2 += 'С: ' + str(
                                            para.time_start.strftime('%H:%M')) + ' до: ' + \
                                                              str(para.time_end.strftime('%H:%M')) + '\n'
                                        schedule_message_2 += str(para.lesson) + '\n'
                                        schedule_message_2 += 'Аудитория: ' + str(para.aud) + '\n'
                                        schedule_message_2 += 'Тип пары: ' + str(para.lessontype) + '\n'
                                        schedule_message_2 += 'Препод: ' + str(para.teacher) + '\n'
                                        schedule_message_2 += '\n\n'

                                        schedule_message_1 += 'Номер пары: ' + str(para.number) + '\n'
                                        schedule_message_1 += 'С: ' + str(para.time_start.strftime('%H:%M')) + ' до: ' + \
                                                              str(para.time_end.strftime('%H:%M')) + '\n'
                                        schedule_message_1 += str(para.lesson) + '\n'
                                        schedule_message_1 += 'Аудитория: ' + str(para.aud) + '\n'
                                        schedule_message_1 += 'Тип пары: ' + str(para.lessontype) + '\n'
                                        schedule_message_1 += 'Препод: ' + str(para.teacher) + '\n'
                                        schedule_message_1 += '\n\n'

                            if len(schedule_message_2) == 0:
                                schedule_message_2 = 'Сегодня пар нет'
                            else:
                                schedule_message_2 = 'Расписание на сегодня:\n\n' + schedule_message_2

                            if len(schedule_message_1) == 0:
                                schedule_message_1 = 'Сегодня пар нет'
                            else:
                                schedule_message_1 = 'Расписание на сегодня:\n\n' + schedule_message_1

                            if msg == 'первая подгруппа':
                                user.mode = 'first_group'
                                sender(id, schedule_message_1, back_key)
                                schedule_message_1 = ''

                            elif msg == 'вторая подгруппа':
                                user.mode = 'second_group'
                                sender(id, schedule_message_2, back_key)
                                schedule_message_2 = ''

                            elif msg == 'назад':
                                sender(id, 'Выберите действие', adm_start_key)
                                user.mode = 'a_start'

                        elif user.mode == 'a_send':

                            if msg == 'назад':
                                sender(id, 'Выберите действие', adm_start_key)
                                user.mode = 'a_start'
                            elif msg == 'ввести текст для рассылки':
                                user.mode = 'check_send'
                                sender(id, 'Введите текст, который будет разослан ❗ВСЕМ❗ пользователям', empty_key)

                        elif user.mode == 'in_adm_panel':
                            if msg == 'да':
                                for user_send in users:
                                    if user_send.status == 'admin':
                                        sender(user_send.id, 'Рассылка выполнена со следующим текстом:', adm_start_key)
                                        sender(user_send.id, s, adm_start_key)
                                        user_send.mode = 'a_start'
                                        # print(user_send.mode, " ", user_send.status)
                                    elif user_send.status == 'common':
                                        sender(user_send.id, 'Вам пришло сообщение с рассылки:', start_key)
                                        sender(user_send.id, s, start_key)
                                        user_send.mode = 'start'
                                        # print(user_send.mode, " ", user_send.status)
                            elif msg == 'нет':
                                sender(id, 'Выберите действие', adm_start_key)
                                user.mode = 'a_start'

                        elif user.mode == 'check_send':
                            s = ''
                            f_msg = vk.messages.getById(message_ids=event.message_id)
                            f_msg = f_msg.get('items')[0]
                            ans_txt_msg = []

                            if f_msg.get('text') != '':
                                ans_txt_msg.append(f_msg.get('text'))

                            get_text(f_msg.get('fwd_messages'))

                            for i in ans_txt_msg:
                                s += i
                                s += '\n'
                            print(s)
                            sender(id, 'Сообщение для рассылки', '')
                            sender(id, s, adm_panel_key)
                            user.mode = 'in_adm_panel'

                        elif user.mode == 'first_group':

                            if msg == 'назад':
                                sender(id, 'Выберите вашу подгруппу', in_schedule_key)
                                user.mode = 'rasp'
                                schedule_message_1 = ''

                        elif user.mode == 'second_group':

                            if msg == 'назад':
                                sender(id, 'Выберите вашу подгруппу', in_schedule_key)
                                user.mode = 'rasp'
                                schedule_message_2 = ''

                    elif user.status == 'common':

                        if user.mode == 'start':

                            if msg == 'расписание':

                                user.mode = 'rasp'
                                sender(id, 'Выберите вашу подгруппу', in_schedule_key)

                            elif msg == 'разработчики':

                                user.mode = 'dev'
                                sender(id, 'Над этим проектом работали:\n'
                                           'vk.com/x_vl_x\n'
                                           'vk.com/mishadukhno\n', empty_key)
                                sender(id, 'Выберите действие', back_key)

                        elif user.mode == 'dev':

                            if msg == 'назад':
                                sender(id, 'Выберите действие', start_key)
                                user.mode = 'start'

                        elif user.mode == 'rasp':

                            cur_time = event.datetime + timedelta(hours=3)  # считает текущее время мск + 4
                            weekday = calendar.day_name[cur_time.weekday()]  # считает текущий день недели
                            # print(cur_time)
                            days = {'Monday': 'Понедельник',
                                    'Tuesday': 'Вторник',
                                    'Wednesday': 'Среда',
                                    'Thursday': 'Четверг',
                                    'Friday': 'Пятница',
                                    'Saturday': 'Суббота ',
                                    'Sunday': 'Воскресенье'
                                    }

                            # print(days.get(weekday)) #Перевод названия дня недели на русский
                            schedule_message_1 = ''
                            schedule_message_2 = ''
                            for para in week_lessons:
                                # print(para.wek_day)
                                if days.get(weekday) == para.wek_day:
                                    if para.podgroup == '(1)':

                                        schedule_message_1 += 'Номер пары: ' + str(para.number) + '\n'
                                        schedule_message_1 += 'С: ' + str(para.time_start.strftime('%H:%M')) + ' до: ' + \
                                                              str(para.time_end.strftime('%H:%M')) + '\n'
                                        schedule_message_1 += str(para.lesson) + '\n'
                                        schedule_message_1 += 'Аудитория: ' + str(para.aud) + '\n'
                                        schedule_message_1 += 'Тип пары: ' + str(para.lessontype) + '\n'
                                        schedule_message_1 += 'Препод: ' + str(para.teacher) + '\n'
                                        schedule_message_1 += '\n\n'

                                    elif para.podgroup == '(2)':

                                        schedule_message_2 += 'Номер пары: ' + str(para.number) + '\n'
                                        schedule_message_2 += 'С: ' + str(
                                            para.time_start.strftime('%H:%M')) + ' до: ' + \
                                                              str(para.time_end.strftime('%H:%M')) + '\n'
                                        schedule_message_2 += str(para.lesson) + '\n'
                                        schedule_message_2 += 'Аудитория: ' + str(para.aud) + '\n'
                                        schedule_message_2 += 'Тип пары: ' + str(para.lessontype) + '\n'
                                        schedule_message_2 += 'Препод: ' + str(para.teacher) + '\n'
                                        schedule_message_2 += '\n\n'

                                    elif para.podgroup == '(1, 2)' or para.podgroup == '':

                                        schedule_message_2 += 'Номер пары: ' + str(para.number) + '\n'
                                        schedule_message_2 += 'С: ' + str(
                                            para.time_start.strftime('%H:%M')) + ' до: ' + \
                                                              str(para.time_end.strftime('%H:%M')) + '\n'
                                        schedule_message_2 += str(para.lesson) + '\n'
                                        schedule_message_2 += 'Аудитория: ' + str(para.aud) + '\n'
                                        schedule_message_2 += 'Тип пары: ' + str(para.lessontype) + '\n'
                                        schedule_message_2 += 'Препод: ' + str(para.teacher) + '\n'
                                        schedule_message_2 += '\n\n'

                                        schedule_message_1 += 'Номер пары: ' + str(para.number) + '\n'
                                        schedule_message_1 += 'С: ' + str(para.time_start.strftime('%H:%M')) + ' до: ' + \
                                                              str(para.time_end.strftime('%H:%M')) + '\n'
                                        schedule_message_1 += str(para.lesson) + '\n'
                                        schedule_message_1 += 'Аудитория: ' + str(para.aud) + '\n'
                                        schedule_message_1 += 'Тип пары: ' + str(para.lessontype) + '\n'
                                        schedule_message_1 += 'Препод: ' + str(para.teacher) + '\n'
                                        schedule_message_1 += '\n\n'

                            if len(schedule_message_2) == 0:
                                schedule_message_2 = 'Сегодня пар нет'
                            else:
                                schedule_message_2 = 'Расписание на сегодня:\n\n' + schedule_message_2

                            if len(schedule_message_1) == 0:
                                schedule_message_1 = 'Сегодня пар нет'
                            else:
                                schedule_message_1 = 'Расписание на сегодня:\n\n' + schedule_message_1

                            if msg == 'первая подгруппа':
                                user.mode = 'first_group'
                                sender(id, schedule_message_1, back_key)
                                schedule_message_1 = ''

                            elif msg == 'вторая подгруппа':
                                user.mode = 'second_group'
                                sender(id, schedule_message_2, back_key)
                                schedule_message_2 = ''

                            elif msg == 'назад':
                                sender(id, 'Выберите действие', start_key)
                                user.mode = 'start'

                        elif user.mode == 'first_group':

                            if msg == 'назад':
                                sender(id, 'Выберите вашу подгруппу', in_schedule_key)
                                user.mode = 'rasp'
                                schedule_message_1 = ''

                        elif user.mode == 'second_group':

                            if msg == 'назад':
                                sender(id, 'Выберите вашу подгруппу', in_schedule_key)
                                user.mode = 'rasp'
                                schedule_message_2 = ''

            change_mode()
