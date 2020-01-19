from vk_api import *
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from settings import token, grp_id
from database import CharactersDatabase
from sqlalchemy import *


# штучка для инициализации клавы
def set_keyboard(*args):
    temp_keyword = VkKeyboard(one_time=True)
    for button in args:
        temp_keyword.add_button(button[0], color=button[1])
        temp_keyword.add_line()
    return temp_keyword


class VkBotLongPollRaw(VkBotLongPoll):
    CLASS_BY_EVENT_TYPE = {}


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
    api = None

    def __init__(self, vk_token=token, group_id=grp_id):
        # bot init
        self.token = vk_token
        self.group_id = group_id

        # db init
        self.database = CharactersDatabase()
        self.connection = self.database.get_connection()
        self.engine = self.database.get_engine()

        # fields
        self.chatting = dict()
        self.to_write = list()
        self.they_writing = list()

    def run(self):
        for event in self.longPoll.listen():
            if event.type == VkBotEventType.MESSAGE_REPLY:
                self.message_reply_handle(event.obj)
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.message_new_handle(event.obj)

    def init_longpol(self):
        self.session = VkApi(
            token="14849e21dd9ac020b16079ce102a8a8985de5b0e2d6f8a45f2522d4dd569fada872331216bcbf981c21e6")
        self.api = self.session.get_api()
        self.longPoll = VkBotLongPollRaw(self.session, self.group_id)

    def message_new_handle(self, obj):
        if not self.database.session.query(self.database.people_stage).filter_by(user_id=obj.get('user_id')).scalar():
            self.init_user(int(obj.get('user_id')))

    # Метод для инициализации юзера(с дефолт. параметрами)
    def init_user(self, user_id):
        user = self.api.users.get(user_id=user_id)[0]
        insertion = self.database.people_stage.insert().values(user_id=user_id, stage=1)
        self.connection.execute(insertion)
        insertion = self.database.people.insert().values(user_id=user_id, name=user['first_name'],
                                                         last_name=user['last_name'])
        self.connection.execute(insertion)
        insertion = self.database.ideal_people.insert().values(user_id=user_id)
        self.connection.execute(insertion)

    # Устаревшая фигня, пока не хочу убирать, если разберусь с MESSAGE_REPLY - верну
    @DeprecationWarning
    def message_reply_handle(self, obj):
        stage = select([self.database.people_stage]).where(
            self.database.people_stage.columns.user_id == obj.get('user_id'))
        if stage is None:
            self.database.people_stage.insert().values(user_id=int(obj.get('user_id')), stage=1)
