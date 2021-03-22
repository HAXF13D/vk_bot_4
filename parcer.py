def get_schedule():
    try:
        import requests
        import json
        from bs4 import BeautifulSoup

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
        }
        url = 'https://ecampus.ncfu.ru/schedule/group/15538'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, features="html.parser")
        item = str(soup.find('script', {'type': 'text/javascript'}).contents[0])

        flag = 0
        stroka = ''
        for i in item:
            if i == '=':
                flag = 1
            elif flag:
                stroka += i
        n = len(stroka)
        stroka = stroka[0:n - 3]
        stroka = stroka.replace('JSON.parse("\\"', '\"')
        stroka = stroka.replace('\\"")', '\"')
        temp_stroka = ''

        for i in range(len(stroka)):
            if stroka[i] == 'T' and stroka[i + 1].isdigit() and stroka[i - 1].isdigit():
                temp_stroka += ' '
            else:
                temp_stroka += stroka[i]
        stroka = temp_stroka

        item = json.loads(stroka).get('weekdays')

    except Exception:
        print('Произошла ошибка функции get_day()')
        item = None
    finally:
        return item


def get_today_schedule(today, item):
    if_lessons_today = False
    try:
        if_lessons_today = False
        if item.get('WeekDay') == today:
            if_lessons_today = True
    except Exception:
        print('Произошла ошибка функции get_today_schedule')
        if_lessons_today = False
    finally:
        return if_lessons_today


def get_cur_lesson(today_lessons, cur_time):
    try:
        cur_lesson = None
        for lesson in today_lessons:
            if (str(cur_time) <= lesson.get('TimeEnd') and str(cur_time) >= lesson.get('TimeBegin')):
                cur_lesson = lesson
    except Exception:
        print('Произошла ошибка функции get_cur_lesson')
        cur_lesson = None
    finally:
        return cur_lesson


# f.write(item)


"""
flag = 0
stroka = ''
for i in item:
    if i == '=':
        flag = 1
    if flag:
        stroka += i
n = len(stroka)
stroka = stroka[2:n-3]
"""
"""
flag = 0
for element in item:
    if element == '=':
        stroka = ''
        flag = 1
    elif element == '<':
        flag = 0
    elif element == '\n':
        pass
    elif flag:
        stroka += element
stroka_length = len(stroka)
stroka= stroka[1: stroka_length - 2]
f.write(item)
f.close()

"""
