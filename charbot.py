from vk_api import *
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard
from settings import token, grp_id
from database import CharactersDatabase
from sqlalchemy import *
from stages import get_stages


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
    stages = None

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
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.message_new_handle(event.obj)

    def init_longpoll(self):
        self.session = VkApi(
            token="14849e21dd9ac020b16079ce102a8a8985de5b0e2d6f8a45f2522d4dd569fada872331216bcbf981c21e6")
        self.api = self.session.get_api()
        self.longPoll = VkBotLongPollRaw(self.session, self.group_id)
        self.stages = get_stages(self.database.connection, self.api, self.database)

    def message_new_handle(self, obj):
        stage = self.database.session.query(self.database.people_stage).filter(
            self.database.people_stage.c.user_id == obj.get('user_id')).first()
        if stage is None:
            self.init_user(int(obj.get('user_id')))
        stage = self.database.session.query(self.database.people_stage).filter(
            self.database.people_stage.c.user_id == obj.get('user_id')).first()
        user_id, stage, answered, transferred = stage
        if stage == len(self.stages):
            self.api.messages.send(peer_id=user_id, random_id=get_random_id(),
                                   message="Ты уже завершил опрос. Попробуй написать в другое время, может быть, "
                                           "у нас появятся новые опросы для тебя!")
            return
        result = self.stages[stage].process(transferred, user_id, obj.get('body'))
        if not transferred:
            self.connection.execute(
                update(self.database.people_stage).where(self.database.people_stage.c.user_id == user_id).values(
                    transferred=True))
        if result > 0:
            req = update(self.database.people_stage).where(self.database.people_stage.c.user_id == user_id).values(
                stage=stage + 1, transferred=True)
            self.connection.execute(req)
            if stage == len(self.stages) - 1:
                self.api.messages.send(peer_id=user_id, random_id=get_random_id(),
                                       message="Спасибо за участие в опросе! Еще увидимся:)",
                                       keyboard=VkKeyboard.get_empty_keyboard())
                return
            self.stages[stage + 1].process(False, user_id, obj.get('body'))

    # Метод для инициализации юзера(с дефолт. параметрами)
    def init_user(self, user_id):
        user = self.api.users.get(user_id=user_id)[0]
        insertion = self.database.people_stage.insert().values(user_id=user_id, stage=0)
        self.connection.execute(insertion)
        insertion = self.database.people.insert().values(user_id=user_id, name=user['first_name'],
                                                         last_name=user['last_name'])
        self.connection.execute(insertion)

    # Устаревшая фигня, пока не хочу убирать, если разберусь с MESSAGE_REPLY - верну
    @DeprecationWarning
    def message_reply_handle(self, obj):
        stage = select([self.database.people_stage]).where(
            self.database.people_stage.columns.user_id == obj.get('user_id'))
        if stage is None:
            self.database.people_stage.insert().values(user_id=int(obj.get('user_id')), stage=1)
