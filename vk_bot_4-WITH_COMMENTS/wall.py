import requests
import vk_api
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll
from requests.exceptions import ConnectionError
import sqlite3 as sqlite

#5241050f0eb555d1feb921c27088dd17bad1309ae42345015f6917f19eca699af47bc241168a39fefd80e Bot testing
#3f6c6e13925f782f50307c6e863350270214547a46a873604fba529c85527088a3beb3eda45bc2a640985 PIJ
#203391000 Bot testing
#200241547 PIJ

groupId = 200241547
token = "3f6c6e13925f782f50307c6e863350270214547a46a873604fba529c85527088a3beb3eda45bc2a640985"
vk = vk_api.VkApi(token = token)
session_api = vk.get_api()
longpoll = VkLongPoll(vk)
try:
    conn = sqlite.connect("date_base.db")
except Exception as e:
    print("Ошибка подключения к бд:")
    print(e)
try:# Соединение с сообществом через токен и айди группы
    data = requests.get('https://api.vk.com/method/groups.getLongPollServer',
                        params={"access_token":token, 'group_id':groupId, "v":5.85}).json()
    data = data["response"]
except ConnectionError as e:
        print(e)

def getIdList(conn):
    try:
        cur = conn.cursor()
        cur.execute("""SELECT userid FROM users;""")
        selection = cur.fetchall()
        return selection
    except Exception as e:
        print("Не удалось получить id пользователей:")
        print(e)

def sendingMsg(newPost, conn):# Функция репоста нового поста
    idList = getIdList(conn)
    attachment = "wall" + str(newPost["owner_id"]) + "_" + str(newPost["id"])
    for line in idList:
        usId = line.split(":")
        vk.method("messages.send",{"user_id": int(usId[0]), "attachment": attachment , "random_id": 0})
    idList.close()

def getAndSendIdea():# Функция ожидания и обработки сообщения с предложением
    while True:
        try:
            response = requests.get('{server}?act=a_check&key={key}&wait=25&mode=2&ts={ts}'.
                                    format(server=data['server'], key=data['key'], ts=data['ts'])).json()
            updates = response['updates']
            if updates:
                for element in updates:
                    if element["type"] == "message_new":
                        message = element["object"]["message"]["text"]
                        devId = [190748248, 190246827]
                        for elem in devId:
                            vk.method("messages.send",{"user_id":elem,"message": message, "random_id": 0})
            data['ts'] = response['ts']
            return
        except ConnectionError as e:
            print(e)
            return

while True: #Основной цикл обработки событий в сообществе
    try:
        response = requests.get('{server}?act=a_check&key={key}&wait=25&mode=2&ts={ts}'.
                                format(server=data['server'], key=data['key'], ts=data['ts'])).json()
        updates = response['updates']
        if updates:
            for element in updates:
                print(element)
                if element["type"] == "wall_post_new":# Обработка репоста нового поста в сообществе
                    sendingMsg(element["object"], conn)
                if element["type"] == "message_new" and element["object"]["message"]["text"].lower() == "предложение":# Обработка отправки сообщения с предложеним разработчикам
                    vk.method("messages.send",{"user_id":element["object"]["message"]["from_id"],"message":"Введите текс полного объяснения вашей идеи, которая будет отправлена разработчикам для реализации"
                                , "random_id": 0})
                    getAndSendIdea();
                    vk.method("messages.send",{"user_id":element["object"]["message"]["from_id"],"message": "Ваше предложение отправленно, спасибо за участие в развитии бота!", "random_id": 0})
        data['ts'] = response['ts']
    except ConnectionError as e:
        print(e)