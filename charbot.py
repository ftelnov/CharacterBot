from vk_api import *
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard
from settings import *
from database import *
from sqlalchemy import *
from stages import StagesProvider
import multiprocessing
import random


class MyVkLongPoll(VkBotLongPoll):
    CLASS_BY_EVENT_TYPE = {}

    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                print('error', e)


start_chat_keyboard = VkKeyboard()
start_chat_keyboard.add_button("Начать чат", color="positive")

end_chat_keyboard = VkKeyboard()
end_chat_keyboard.add_button("Завершить чат", color="negative")


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
    process = None
    waiting_users = []

    def match_users(self):

        while True:
            while len(self.waiting_users) >= 2:
                first, second = random.sample(range(0, len(self.waiting_users)), 2)
                user_first, user_second = self.waiting_users[first], self.waiting_users[second]
                user_first.in_chat = True
                user_first.with_user = user_second.id
                user_second.in_chat = True
                user_second.with_user = user_second.id
                self.waiting_users.pop(first)
                self.waiting_users.pop(second)
                self.api.messages.send(peer_id=user_first.id, message="Отлично, мы нашли вам собеседника! Общайтесь:)",
                                       random_id=get_random_id(), keyboard=end_chat_keyboard.get_keyboard())
                self.api.messages.send(peer_id=user_second.id, message="Отлично, мы нашли вам собеседника! Общайтесь:)",
                                       random_id=get_random_id(), keyboard=end_chat_keyboard.get_keyboard())
                self.session.commit()

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
        self.process = multiprocessing.Process(target=self.match_users)
        self.process.start()

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

    def handle_chating_user_message(self, user, message):
        text = message['text']
        if not user.in_chat and text == "Начать чат":
            self.api.messages.send(peer_id=user.id, message="Подожди, пока мы подберем тебе собеседника!",
                                   random_id=get_random_id())
            self.waiting_users.append(user)
        if str(text).capitalize() == "Завершить чат":
            self.api.messages.send(peer_id=user.id,
                                   message="Завершаю чат. Когда надумаешь - напиши `Начать чат`, или нажми "
                                           "соответствующую кнопку",
                                   keyboard=start_chat_keyboard.get_keyboard())
            user.in_chat = False
            self.session.commit()

        self.api.messages.send(peer_id=user.with_user, message=text, random_id=get_random_id())

    def message_new_handle(self, obj):
        message = obj['message']
        user_id = int(message['from_id'])
        message_text = message['text']
        user = self.session.query(User).filter_by(id=user_id).first()
        if user is None:
            self.init_user(user_id)
            user = self.session.query(User).filter_by(id=user_id).first()

        if user.stage == -1:
            if message_text.capitalize() == "Начать":
                user.stage = 0
                self.session.commit()
            else:
                return
        if user.need_renew:
            if message_text == "Повторить":
                self.clean_user_data(user_id)
            else:
                self.api.messages.send(peer_id=user_id, message=strings["need_renew"], random_id=get_random_id())
                return
        if user.part == 1:
            self.handle_chating_user_message(user, message)
            return
        stage, transferred = user.stage, user.stage_transferred
        if stage >= len(self.stages):
            self.api.messages.send(peer_id=user_id, message=strings['finished'],
                                   random_id=get_random_id())
            return
        result = self.stages[stage].process(transferred, user_id, message_text)
        if not transferred:
            user.stage_transferred = True
        if result == -7:
            stage -= 1
            if stage < 0:
                stage = 0
            else:
                if user.results[-1] == '+':
                    setattr(user, self.stages[stage - 1].parameter,
                            getattr(user, self.stages[stage - 1].parameter) - 1)
                user.results = user.results[:-1]
            user.stage = stage
            user.stage_transferred = True
            self.session.commit()
            self.stages[stage].process(False, user_id, message_text)
            return
        if result > 0:
            user.stage += 1
            if stage >= len(self.stages) - 1:
                self.check_answers(user_id)
                return
            self.stages[stage + 1].process(False, user_id, "None")
        self.session.commit()

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
        user.part = 1
        self.session.commit()
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
                result += strings["your_level_neuro"] + ranges_neuro[level] + ". Спасибо за участие. Сейчас ты можешь " \
                                                                              "початиться с пользователями в " \
                                                                              "анонимном режиме:)"
        keyboard = VkKeyboard()
        keyboard.add_button("Начать чат", color="positive")
        self.api.messages.send(peer_id=user_id, message=result, random_id=get_random_id(),
                               keyboard=keyboard.get_keyboard())

    # Метод для инициализации юзера(с дефолт. параметрами)
    def init_user(self, user_id):
        vk_user = self.api.users.get(user_id=user_id)[0]
        new_user = User(id=user_id, first_name=vk_user['first_name'], last_name=vk_user['last_name'])
        self.session.add(new_user)
