from vk_api import *
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard
from settings import *
from database import *
from sqlalchemy import *
from stages import StagesProvider


class MyVkLongPoll(VkLongPoll):
    CLASS_BY_EVENT_TYPE = {}

    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                print('error', e)


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
            token=strings['token'])
        self.api = self.api_session.get_api()
        self.longPoll = MyVkLongPoll(self.api_session, self.group_id)
        self.stageProvider = StagesProvider(self.session, self.api)
        self.stages = self.stageProvider.get_instance()

    def clean_user_data(self, user_id):
        user = self.session.query(User).filter_by(id=user_id).first()
        user.need_renew = False
        user.extroversion = 0
        user.neurotism = 0
        user.stage = 2
        user.lie = 0
        user.results = ""
        user.stage_transferred = False
        self.session.commit()

    def message_new_handle(self, obj):
        try:
            user_id = int(obj.get('user_id'))
            user = self.session.query(User).filter_by(id=user_id).first()
            if user is None:
                self.init_user(user_id)
            if user.stage == 0 and obj.get("body").capitalize() == "Начать":
                user.stage = 1
                self.session.commit()
            if user.need_renew:
                if obj.get('body') == "Повторить":
                    self.clean_user_data(user_id)
                else:
                    self.api.messages.send(peer_id=user_id, message=strings["need_renew"], random_id=get_random_id())
                    return
            stage, transferred = user.stage, user.stage_transferred
            if stage >= len(self.stages):
                self.api.messages.send(peer_id=user_id, message=strings['finished'],
                                       random_id=get_random_id())
                return
            result = self.stages[stage - 1].process(transferred, user_id, obj.get("body"))
            if not transferred:
                user.stage_transferred = True
            if result == -7:
                stage -= 1
                if stage < 1:
                    stage = 1
                else:
                    if user.results[-1] == '+':
                        setattr(user, self.stages[stage - 1].parameter,
                                getattr(user, self.stages[stage - 1].parameter) - 1)
                    user.results = user.results[:-1]
                user.stage = stage
                user.stage_transferred = True
                self.session.commit()
                self.stages[stage].process(False, user_id, obj.get("body"))
                return
            if result > 0:
                user.stage += 1
                if stage >= len(self.stages) - 1:
                    self.check_answers(user_id)
                    return
                self.stages[stage + 1].process(False, user_id, "None")
            self.session.commit()
        except Exception as exc:
            with open('data/log.txt', "a") as file:
                file.write("\n" + str(exc) + "\n")

    def check_answers(self, user_id):
        user = self.session.query(User).filter_by(id=user_id).first()
        extroversion, neurotism, lie = user.extroversion, user.neurotism, user.lie
        if lie > 4:
            keyboard = VkKeyboard(one_time=False)
            keyboard.add_button("Повторить", "primary")
            self.api.messages.send(peer_id=user_id,
                                   message=strings['high_lie'],
                                   random_id=get_random_id(), keyboard=keyboard.get_keyboard())
            user.need_renew = True
            self.session.commit()
            return
        result = ""
        extro = user.extroversion
        neuro = user.neurotism
        for level in ranges_extro:
            first, second = level
            if first < extro <= second:
                result += strings["your_level_extro"] + ranges_extro[level] + ". "
                break
        for level in ranges_neuro:
            first, second = level
            if first < neuro <= second:
                result += strings["your_level_neuro"] + ranges_neuro[level] + ". Спасибо за участие. Еще увидимся:)"
        self.api.messages.send(peer_id=user_id, message=result, random_id=get_random_id(),
                               keyboard=VkKeyboard.get_empty_keyboard())

    # Метод для инициализации юзера(с дефолт. параметрами)
    def init_user(self, user_id):
        vk_user = self.api.users.get(user_id=user_id)[0]
        new_user = User(id=user_id, first_name=vk_user['first_name'], last_name=vk_user['last_name'])
        self.session.add(new_user)
