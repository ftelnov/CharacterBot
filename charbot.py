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
from requests.adapters import HTTPAdapter


class MyHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        super(MyHTTPAdapter, self).__init__(*args, **kwargs)

    def send(self, *args, **kwargs):
        return super(MyHTTPAdapter, self).send(*args, **kwargs)


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
    waiting_users = multiprocessing.Manager().list()

    def match_users(self):
        while True:
            while len(self.waiting_users) >= 2:
                first, second = random.sample(range(0, len(self.waiting_users)), 2)
                user_first, user_second = self.session.query(User).filter_by(
                    id=self.waiting_users[first].id).first(), self.session.query(User).filter_by(
                    id=self.waiting_users[second].id).first()
                self.waiting_users.pop(first)
                self.waiting_users.pop(second - 1)
                user_first.in_chat = True
                user_first.with_user = user_second.id
                user_second.in_chat = True
                user_second.with_user = user_first.id
                new_chat = Chat(first_user=user_first.id, second_user=user_second.id)
                self.session.add(new_chat)
                self.session.commit()
                chat = self.session.query(Chat).filter_by(first_user=user_first.id, second_user=user_second.id).first()
                user_first.last_conv = chat.id
                user_second.last_conv = chat.id
                self.api.messages.send(user_ids=[user_second.id, user_first.id],
                                       message="Отлично, мы нашли вам собеседника! Общайтесь:)",
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
        with open('http.txt') as file:
            http = list(map(lambda x: 'http://' + str(x).rstrip('\n') + '/', file.readlines()))
        with open('https.txt') as file:
            https = list(map(lambda x: 'https://' + str(x).rstrip('\n') + '/', file.readlines()))
        self.api_session.http.mount('https://', MyHTTPAdapter(max_retries=10))
        self.api = self.api_session.get_api()
        self.longPoll = MyVkLongPoll(self.api_session, self.group_id)
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
        if user.need_rate:
            try:
                int(text)
            except Exception:
                return
            if 1 <= int(text) <= 10:
                chat = self.session.query(Chat).filter_by(id=user.last_conv)
                user.need_rate = False
                if user.id == chat.first().first_user:
                    chat.update({'rate_first_user': int(text)})
                else:
                    chat.update({'rate_second_user': int(text)})
                self.session.commit()
                self.api.messages.send(peer_id=user.id, message="Спасибо за оценку! Попутного ветра в чатах:)",
                                       random_id=get_random_id(), keyboard=start_chat_keyboard.get_keyboard())
                return

        if not user.in_chat and text == "Начать чат":
            self.api.messages.send(peer_id=user.id, message="Подожди, пока мы подберем тебе собеседника!",
                                   random_id=get_random_id(), keyboard=VkKeyboard.get_empty_keyboard())
            self.waiting_users.append(user)
        if str(text).capitalize() == "Завершить чат":
            self.api.messages.send(peer_id=user.id, random_id=get_random_id(),
                                   message=strings['you_end_conv'],
                                   keyboard=start_chat_keyboard.get_keyboard())
            self.api.messages.send(peer_id=user.with_user, random_id=get_random_id(),
                                   message=strings['teammate_end_conv'], keyboard=start_chat_keyboard.get_keyboard())
            user_with = self.session.query(User).filter_by(id=user.with_user).first()
            user_with.in_chat = False
            user_with.need_rate = True
            user.need_rate = True
            user.in_chat = False
            self.session.commit()
        if user.in_chat:
            self.api.messages.send(peer_id=user.with_user, message=text, random_id=get_random_id())

    def message_new_handle(self, obj):
        message = obj['message']
        user_id = int(message['from_id'])
        message_text = message['text']
        user = self.session.query(User).filter_by(id=user_id).first()
        if user is None:
            self.init_user(user_id)
            user = self.session.query(User).filter_by(id=user_id).first()
        if not user.received_hello and message_text == "Начать":
            user.received_hello = True
            self.session.commit()
            self.api.messages.send(peer_id=user.id, message=strings['lets_start'], random_id=get_random_id(),
                                   attachment="photo-190919664_457239017")
            return
        if user.part == 1:
            self.handle_chating_user_message(user, message)
            return
        try:
            if user.chosen_image == -1 and 1 <= int(message_text) <= 10:
                user.chosen_image = int(message_text)
                user.part = 1
                self.api.messages.send(peer_id=user.id, message=strings['passed_to_chat'],
                                       random_id=get_random_id(),
                                       keyboard=start_chat_keyboard.get_keyboard())
                self.session.commit()
        except Exception as exc:
            pass

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
        self.session.commit()
