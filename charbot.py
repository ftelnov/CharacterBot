from vk_api import *
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard
from settings import token, grp_id
from database import CharactersDatabase
from sqlalchemy import *
from Models import User
from stages import get_stages


class VkBotLongPollRaw(VkBotLongPoll):
    CLASS_BY_EVENT_TYPE = {}


class CharBot:
    longPoll = None
    database = None
    session = None
    api = None
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
        self.session = self.database.session

    def run(self):
        for event in self.longPoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.message_new_handle(event.obj)

    def init_longpoll(self):
        self.session = VkApi(
            token="6cc187e46a2645689d3e41ad3439a3513a15dd25a10efec596a7800f125ddd4f4069b344406fcee180654")
        self.api = self.session.get_api()
        self.longPoll = VkBotLongPollRaw(self.session, self.group_id)
        self.stages = get_stages(self.database.connection, self.api, self.database)

    def message_new_handle(self, obj):
        user_id = obj.get('user_id')
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if user is None:
            self.init_user(user_id)
        user = self.session.query(User).filter_by(user_id=user_id).first()
        stage, transferred = user.stage, user.stage_transferred


    # Метод для инициализации юзера(с дефолт. параметрами)
    def init_user(self, user_id):
        vk_user = self.api.users.get(user_id=user_id)[0]
        new_user = User(user_id, vk_user['first_name'], vk_user['last_name'])
        self.session.add(new_user)

    # Устаревшая фигня, пока не хочу убирать, если разберусь с MESSAGE_REPLY - верну
    @DeprecationWarning
    def message_reply_handle(self, obj):
        stage = select([self.database.people_stage]).where(
            self.database.people_stage.columns.user_id == obj.get('user_id'))
        if stage is None:
            self.database.people_stage.insert().values(user_id=int(obj.get('user_id')), stage=1)
