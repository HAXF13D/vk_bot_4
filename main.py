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

UP_DAY = 'Monday'

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

STATUS_ADM = 'admin'
STATUS_COM = 'common'

MODE_0 = 'start'
MODE_1 = 'a_start'
MODE_2 = 'rasp'
MODE_3 = 'dev'
MODE_4 = 'a_send'
MODE_5 = 'first_group'
MODE_6 = 'second_group'
MODE_7 = 'in_adm_panel'
MODE_8 = 'check_send'

START_MSG = ['начать', '/start', 'start', '/начать']


class Attachments:

    def __init__(self, attachment_type, owner_id, doc_id, access_key):
        self.attachment_type = attachment_type
        self.owner_id = owner_id
        self.doc_id = doc_id
        self.access_key = access_key

    def make_attachment(self):
        if self.access_key is not None:
            return str(self.attachment_type) + str(self.owner_id) + '_' + str(self.doc_id) + '_' + str(self.access_key)
        else:
            return str(self.attachment_type) + str(self.owner_id) + '_' + str(self.doc_id)


class User:

    def __init__(self, id, status, mode):
        self.id = id
        self.status = status
        self.mode = mode


class Today_Schedule:

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


class Week_Schedule:

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
    if line != '':
        users.append(User(int(line[0]), line[1], line[2]))
f.close()


def schedule_message_check(schedule_message):
    if len(schedule_message) == 0:
        result = 'Сегодня пар нет'
    else:
        result = 'Расписание на сегодня:\n\n' + schedule_message

    return result


def get_schedule_message(para):
    result = ''
    result += 'Номер пары: ' + str(para.number) + '\n'
    result += 'С: ' + str(para.time_start.strftime('%H:%M')) + ' до: ' + \
              str(para.time_end.strftime('%H:%M')) + '\n'
    result += str(para.lesson) + '\n'
    result += 'Аудитория: ' + str(para.aud) + '\n'
    result += 'Тип пары: ' + str(para.lessontype) + '\n'
    result += 'Препод: ' + str(para.teacher) + '\n'
    result += 'Ссылка БББ: ' + get_link(get_links(), str(para.teacher))
    result += '\n\n'
    return result


def get_keyboard(state, buts):  # функция создания клавиатур
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
    vk_session.method('messages.send',
                      {'user_id': id,
                       'message': text,
                       'random_id': 0,
                       'keyboard': key,
                       'dont_parse_links': 1,
                       'attachment': attachment
                       })


def get_text(msg):  # Функция преобразования пересланых сообщений в массив строк
    try:
        if msg is not None:
            for i in msg:
                if i.get('text') != '':
                    ans_txt_msg.append(i.get('text'))
                get_text(i.get('fwd_messages'))
    except Exception:
        print('Произошла ошибка в функции get_text')


def get_attachments(item):
    try:
        if item is not None:
            for i in item:
                if len(i.get('attachments')) != 0:
                    ans_attach.append(i.get('attachments'))
                get_attachments(i.get('fwd_messages'))
    except Exception:
        print('Произошла ошибка в функции get_attachments')


def change_mode():
    f = open(file, mode='w', encoding='utf-8')
    for user in users:
        f.write(f"{user.id}:{user.status}:{user.mode}:\n")
    f.close()


def change_user_mode(user, str_mode, msg, keyboard, attachment):
    user.mode = str_mode
    sender(user.id, msg, keyboard, attachment)


def change_user_mode_2(user, str_mode, msg1, msg2, keyboard, attachment1, attachment2):
    user.mode = str_mode
    sender(user.id, msg1, keyboard, attachment1)
    sender(user.id, msg2, keyboard, attachment2)


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
final_attachment = ''
flag = True
first_start = True
week_lessons = []

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            id = event.user_id
            msg = event.text.lower()
            time = event.datetime + timedelta(hours=3)
            print(time)
            update_day = calendar.day_name[time.weekday()]
            if (update_day == UP_DAY and flag) or first_start:
                flag = False
                first_start = False
                week_lessons = []
                schedule = get_schedule()
                if schedule is not None:
                    for item_day in schedule:
                        for day in DAY_OF_WEEK:
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

            elif update_day != UP_DAY:
                flag = True

            if msg in START_MSG:
                flag1 = True
                for user in users:
                    print(user.status)
                    if user.id == id:
                        print('YES')

                        if user.status == STATUS_ADM:
                            change_user_mode(user, MODE_1, CHO0SE_ACTION, adm_start_key, [])

                        else:
                            change_user_mode(user, MODE_0, CHO0SE_ACTION, start_key, [])

                        flag1 = False

                if flag1:
                    users.append(User(id, STATUS_COM, MODE_0))
                    f = open(file, mode='a', encoding='utf-8')
                    f.write(str(id) + ':' + STATUS_COM + ':' + MODE_0 + '\n')
                    f.close()

                    sender(int(id), CHO0SE_ACTION, start_key, [])

            for user in users:
                if user.id == id:

                    if user.status == STATUS_ADM:

                        if user.mode == MODE_1:
                            if msg == 'расписание':
                                change_user_mode(user, MODE_2, CHO0SE_GROUP, in_schedule_key, [])

                            elif msg == 'разработчики':

                                change_user_mode_2(user, MODE_3, DEV_MSG, CHO0SE_ACTION, back_key, [], [])

                            elif msg == 'рассылка':

                                change_user_mode(user, MODE_4, WARNING_MSG, ready_send, [])

                        elif user.mode == MODE_3:

                            if msg == 'назад':
                                change_user_mode(user, MODE_1, CHO0SE_ACTION, adm_start_key, [])

                        elif user.mode == MODE_2:

                            cur_time = event.datetime + timedelta(hours=3)  # считает текущее время мск + 4
                            weekday = calendar.day_name[cur_time.weekday()]  # считает текущий день недели
                            # print(cur_time)

                            # print(DAYS.get(weekday)) #Перевод названия дня недели на русский
                            schedule_message_1 = ''
                            schedule_message_2 = ''
                            for para in week_lessons:
                                print(para.wek_day)
                                if DAYS.get(weekday) == para.wek_day:
                                    if para.podgroup == '(1)':
                                        schedule_message_1 += get_schedule_message(para)

                                    elif para.podgroup == '(2)':
                                        schedule_message_2 += get_schedule_message(para)

                                    elif para.podgroup == '(1, 2)' or para.podgroup == '':
                                        schedule_message_2 += get_schedule_message(para)
                                        schedule_message_1 += get_schedule_message(para)

                            schedule_message_2 = schedule_message_check(schedule_message_2)
                            schedule_message_1 = schedule_message_check(schedule_message_1)

                            if msg == 'первая подгруппа':
                                change_user_mode(user, MODE_5, schedule_message_1, back_key, [])

                            elif msg == 'вторая подгруппа':
                                change_user_mode(user, MODE_6, schedule_message_2, back_key, [])

                            elif msg == 'назад':
                                change_user_mode(user, MODE_1, CHO0SE_ACTION, adm_start_key, [])

                        elif user.mode == MODE_4:

                            if msg == 'назад':
                                change_user_mode(user, MODE_1, CHO0SE_ACTION, adm_start_key, [])

                            elif msg == 'ввести текст для рассылки':
                                change_user_mode(user, MODE_8, MAILING_MSG, empty_key, [])

                        elif user.mode == MODE_7:
                            if msg == 'да':
                                for user_send in users:
                                    if user_send.status == STATUS_ADM:
                                        change_user_mode_2(user_send, MODE_1, MAILING_ADM_MSG, s, adm_start_key, '', final_attachment)

                                    elif user_send.status == STATUS_COM:
                                        change_user_mode_2(user_send, MODE_0, MAILING_COM_MSG, s, start_key, '', final_attachment)

                            elif msg == 'нет':
                                change_user_mode(user, MODE_1, CHO0SE_ACTION, adm_start_key, [])

                        elif user.mode == 'check_send':
                            s = ''
                            final_attachment = ""
                            f_msg = vk.messages.getById(message_ids=event.message_id)
                            f_msg = f_msg.get('items')

                            ans_attach = []
                            get_attachments(f_msg)
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

                            for attachment in our_attachment:
                                final_attachment += attachment.make_attachment() + ','
                            final_attachment = final_attachment.strip(',')

                            f_msg = f_msg[0]
                            ans_txt_msg = []
                            if f_msg.get('text') != '':
                                ans_txt_msg.append(f_msg.get('text'))

                            get_text(f_msg.get('fwd_messages'))

                            for txt in ans_txt_msg:
                                s += txt
                                s += '\n'
                            change_user_mode_2(user, MODE_7, MSG_FOR_MAILING, s, adm_panel_key, '', final_attachment)
                        elif user.mode == MODE_5 or user.mode == MODE_6:

                            if msg == 'назад':
                                change_user_mode(user, MODE_2, CHO0SE_GROUP, in_schedule_key, [])

                    elif user.status == STATUS_COM:

                        if user.mode == MODE_0:

                            if msg == 'расписание':
                                change_user_mode(user, MODE_2, CHO0SE_GROUP, in_schedule_key, [])

                            elif msg == 'разработчики':
                                change_user_mode_2(user, MODE_3, DEV_MSG, CHO0SE_ACTION, back_key, [], [])

                        elif user.mode == MODE_3:

                            if msg == 'назад':
                                change_user_mode(user, MODE_0, CHO0SE_ACTION, start_key, [])

                        elif user.mode == MODE_2:

                            cur_time = event.datetime + timedelta(hours=3)  # считает текущее время мск + 4
                            weekday = calendar.day_name[cur_time.weekday()]  # считает текущий день недели
                            # print(cur_time)
                            # print(DAYS.get(weekday)) #Перевод названия дня недели на русский
                            schedule_message_1 = ''
                            schedule_message_2 = ''
                            for para in week_lessons:
                                # print(para.wek_day)
                                if DAYS.get(weekday) == para.wek_day:
                                    if para.podgroup == '(1)':
                                        schedule_message_1 += get_schedule_message(para)

                                    elif para.podgroup == '(2)':
                                        schedule_message_2 += get_schedule_message(para)

                                    elif para.podgroup == '(1, 2)' or para.podgroup == '':
                                        schedule_message_2 += get_schedule_message(para)
                                        schedule_message_1 += get_schedule_message(para)

                            schedule_message_2 = schedule_message_check(schedule_message_2)
                            schedule_message_1 = schedule_message_check(schedule_message_1)

                            if msg == 'первая подгруппа':
                                change_user_mode(user, MODE_5, schedule_message_1, back_key, [])

                            elif msg == 'вторая подгруппа':
                                change_user_mode(user, MODE_6, schedule_message_2, back_key, [])

                            elif msg == 'назад':
                                change_user_mode(user, MODE_0, CHO0SE_ACTION, start_key, [])

                        elif user.mode == MODE_5 or user.mode == MODE_6:

                            if msg == 'назад':
                                change_user_mode(user, MODE_2, CHO0SE_GROUP, in_schedule_key, [])

            change_mode()
