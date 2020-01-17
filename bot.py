import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from time import sleep
from datetime import datetime, timedelta
from random import choice
import os
import sqlite3
from settings import *
from questions import *
import sqlalchemy as db

engine = db.create_engine(db_address)  # создали бдшку по адресу из настроек
connection = engine.connect()

user = vk_api.VkApi(token=token)
vk = user.get_api()
chatting = dict()
to_write = list()
they_writing = list()

# клавиатуры
# да-нет
yes_no = VkKeyboard(one_time=True)
yes_no.add_button('Да, я хочу общаться', color=VkKeyboardColor.POSITIVE)
yes_no.add_line()
yes_no.add_button('Нет, не надо', color=VkKeyboardColor.NEGATIVE)

# Создаем data.db если нету
# столбцы from_id, about_id, plaintext
# откого, о ком, текст отзыва
flag = 0



def main():
    longpoll = VkBotLongPoll(user, group_id)

    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:

                body = event.object.message['text']
                current_id = event.object.message['from_id']

                if current_id in they_writing:
                    to = chatting[current_id][0]
                    chatting[current_id].pop(0)
                    they_writing.pop(0)

                    vk.messages.send(peer_id=current_id,
                                     message="Спасибо за помощь, если хочешь пообщаться еще, то напиши 'Начать'",
                                     random_id=get_random_id())

                    cur.execute(f"INSERT INTO REVIEW VALUES({current_id}, {to}, '{body}')")
                    con.commit()

                elif body == 'Начать':
                    vk.messages.send(peer_id=current_id,
                                     message=privet,
                                     random_id=get_random_id(), keyboard=yes_no.get_keyboard())
                elif body == 'Нет, не надо':
                    vk.messages.send(peer_id=current_id,
                                     message="Ну ладно, но жди, тебе могут написать",
                                     random_id=get_random_id(), keyboard=yes_no.get_keyboard())
                elif body == 'Да, я хочу общаться':
                    list_users = vk.groups.getMembers(group_id=160204503, fields='first_name', name_case='ins')["items"]
                    human = choice(list_users)
                    itr = 0
                    no_talk = 0
                    while 'deactivated' in human or human['id'] == current_id or \
                            (current_id in chatting and human['id'] in chatting[current_id]):
                        human = choice(list_users)
                        itr += 1
                        if itr > 2 * len(list_users):
                            no_talk = True
                            break
                    if no_talk:
                        vk.messages.send(peer_id=current_id,
                                         message="Не с кем поговорить, прости(",
                                         random_id=get_random_id())
                    else:
                        vk.messages.send(peer_id=current_id,
                                         message=greeting.format(human['last_name'], human["first_name"]),
                                         random_id=get_random_id())
                        if current_id not in chatting:
                            chatting[current_id] = list()
                        chatting[current_id].append(human['id'])
                        to_write.append([datetime.now(), current_id, human['id']])
                else:
                    vk.messages.send(peer_id=current_id,
                                     message="Напиши 'Начать', чтобы найти собеседника",
                                     random_id=get_random_id())

            while len(to_write) > 0 and datetime.now() - to_write[0][0] > timedelta(seconds=2):  #
                info = vk.users.get(user_id=to_write[0][2], name_case='ins')
                info = info[0]
                vk.messages.send(peer_id=to_write[0][1],
                                 message=after_3days.format(info['last_name'], info['first_name']),
                                 random_id=get_random_id())
                they_writing.append(to_write[0][1])
                to_write.pop(0)

    except Exception as e:
        cur.close()
        print(e)
        sleep(0.5)


if __name__ == "__main__":
    main()

'''
Пользователь пишет "Начать"
Мы ему предлагаем рандомный id из группы пообщаться
Через 3 дня его просят написать отзыв о человеке, который сохраняется в дата.дб
'''
