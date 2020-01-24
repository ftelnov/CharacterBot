from vk_api import *
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard
from settings import token, grp_id
from database import *
from sqlalchemy import *
from stages import StagesProvider


class VkBotLongPollRaw(VkBotLongPoll):
    CLASS_BY_EVENT_TYPE = {}


class CharBot:
    longPoll = None
    session = None
    api = None
    token = None
    group_id = None
    api = None
    stages = None
    api_session = None
    stageProvider = None

    def __init__(self, vk_token=token, group_id=grp_id):
        # bot init
        self.token = vk_token
        self.group_id = group_id

        self.session = session

    def run(self):
        for event in self.longPoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.message_new_handle(event.obj)

    def init_longpoll(self):
        self.api_session = VkApi(
            token="6cc187e46a2645689d3e41ad3439a3513a15dd25a10efec596a7800f125ddd4f4069b344406fcee180654")
        self.api = self.api_session.get_api()
        self.longPoll = VkBotLongPollRaw(self.api_session, self.group_id)
        self.stageProvider = StagesProvider(self.session, self.api)
        self.stages = self.stageProvider.get_instance()

    def message_new_handle(self, obj):
        user_id = int(obj.get('user_id'))
        user = self.session.query(User).filter_by(id=user_id).first()
        if user is None:
            self.init_user(user_id)
        user = self.session.query(User).filter_by(id=user_id).first()
        stage, transferred = user.stage, user.stage_transferred
        if stage >= len(self.stages):
            self.api.messages.send(peer_id=user_id, message="Извини, для тебя пока ничего нет, заглядывай позже!",
                                   random_id=get_random_id())
            return
        result = self.stages[stage].process(transferred, user_id, obj.get("body"))
        if not transferred:
            user.stage_transferred = True
        if result == -7:
            stage -= 1
            if stage < 2:
                stage = 2
            else:
                if user.results[-1] == '+':
                    setattr(user, self.stages[stage].parameter, getattr(user, self.stages[stage].parameter) - 1)
            user.stage = stage
            user.stage_transferred = True
            self.session.commit()
            self.stages[stage].process(False, user_id, obj.get("body"))
            return
        if result > 0:
            user.stage += 1
            if stage >= len(self.stages) - 1:
                self.api.messages.send(peer_id=user_id, message="Спасибо за участие в опросе! Еще увидимся:)",
                                       random_id=get_random_id())
                return
            self.stages[stage + 1].process(False, user_id, "None")
        self.session.commit()

    # Метод для инициализации юзера(с дефолт. параметрами)
    def init_user(self, user_id):
        vk_user = self.api.users.get(user_id=user_id)[0]
        new_user = User(id=user_id, first_name=vk_user['first_name'], last_name=vk_user['last_name'])
        self.session.add(new_user)
