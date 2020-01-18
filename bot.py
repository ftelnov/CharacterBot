import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from time import sleep
from datetime import datetime, timedelta
from random import choice
from settings import *
from questions import *
from database import *

db = CharactersDatabase()
connection = db.get_connection()
engine = db.get_engine()
peoples = db.get_peoples()
messages = db.get_messages()

session = vk_api.VkApi(token=token)
api = session.get_api()
chatting = dict()
to_write = list()
they_writing = list()

yes_no = VkKeyboard(one_time=True)
yes_no.add_button('Да, я хочу общаться', color=VkKeyboardColor.POSITIVE)
yes_no.add_line()
yes_no.add_button('Нет, не надо', color=VkKeyboardColor.NEGATIVE)

flag = 0





if __name__ == "__main__":
    main()

'''
Пользователь пишет "Начать"
Мы ему предлагаем рандомный id из группы пообщаться
Через 3 дня его просят написать отзыв о человеке, который сохраняется в дата.дб
'''
