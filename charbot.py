from vk_api import *
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from database import *


# штучка для инициализации клавы
def set_keyboard(*args):
    temp_keyword = VkKeyboard(one_time=True)
    for button in args:
        temp_keyword.add_button(button[0], color=button[1])
        temp_keyword.add_line()
    return temp_keyword


class CharBot:
    longPoll = None
    database = None
    database_connection = None
    database_engine = None
    session = None
    api = None
    chatting = None
    to_write = None
    they_writing = None
    token = None
    group_id = None

    def __init__(self, vk_token=token, group_id=grp_id):
        self.token = vk_token
        self.group_id = group_id
        self.session = VkApi(self.token)
        self.api = self.session.get_api()
        self.database = CharactersDatabase()
        self.connection = self.database.get_connection()
        self.engine = self.database.get_engine()
        self.chatting = dict()
        self.to_write = list()
        self.they_writing = list()
        self.longPoll = VkBotLongPoll(self.session, self.group_id)

    def run(self):
        for event in self.longPoll.listen():
            if event.type == VkBotEventType.MESSAGE_REPLY:
                print(1)
            if event.type == VkBotEventType.MESSAGE_NEW
