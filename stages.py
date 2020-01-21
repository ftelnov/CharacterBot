from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from sqlalchemy import *

questions = [
    "Начнем наш диалог?",
    "Привет! Хочешь пообщаться, а заодно и внести свой вклад в науку?:)",
    "Ты любишь цветы?"
]
POSITIVE_BUTTON = ("Да", "positive")
NEGATIVE_BUTTON = ("Нет", "negative")


def get_stages(connection, api, db):
    stages = [StageWithKeyboard(api, questions[0], POSITIVE_BUTTON, NEGATIVE_BUTTON),
              StageWithKeyboard(api, questions[1], POSITIVE_BUTTON, NEGATIVE_BUTTON)]
    with open("data/questions.txt", encoding='UTF-8') as file:
        for line in file.readlines():
            quest, row, value = line.split("|")
            stages.append(StageWithKeyboardAizenk(connection, api, quest, db.people, row, value))
    return stages


class DefaultStage:
    text = None
    api = None

    def __init__(self, api, text, *args):
        pass

    def send(self, user_id):
        pass

    def process(self, code, user_id, answer):
        pass


class StageWithKeyboard(DefaultStage):
    keyboard = None
    buttons = None

    def set_keyboard(self, *args):
        self.keyboard = VkKeyboard(one_time=False)
        buttons = list(*args)
        for i in range(len(buttons)):
            button = buttons[i]
            self.keyboard.add_button(button[0], color=button[1])

    def __init__(self, api, text, *args):
        super().__init__(api, text, *args)
        self.text = text
        self.api = api
        self.set_keyboard(args)
        self.buttons = args

    def send(self, user_id):
        self.api.messages.send(peer_id=user_id, random_id=get_random_id(), keyboard=self.keyboard.get_keyboard(),
                               message=self.text)

    def process(self, code, user_id, answer):
        if not code:
            self.send(user_id)
            return -1
        for button in self.buttons:
            if button[0] == answer.capitalize():
                if button[1] == 'negative':
                    return -1
                else:
                    return 1
        self.api.messages.send(peer_id=user_id, random_id=get_random_id(), message="Извини, я тебя не понимаю!")
        return 0


class StageWithKeyboardAizenk(StageWithKeyboard):
    session = None
    value = None

    def __init__(self, session, value, api, text):
        super().__init__(api, text, POSITIVE_BUTTON, NEGATIVE_BUTTON)
        self.connection = session
        self.value = value

    def process(self, code, user_id, answer):
        if not code:
            self.send(user_id)
            return -1
        for button in self.buttons:
            if button[0] == answer.capitalize():
                if (button[1] == 'negative' and int(self.value) == -1) or (
                        button[1] == 'positive' and int(self.value) == 1):
                    if self.db_row == "extroversion":
                        self.connection.execute(self.db_table.update(self.db_table.c.user_id == user_id).values(
                            extroversion=self.db_table.c.extroversion + 1))
                    elif self.db_row == "lie":
                        self.connection.execute(self.db_table.update(self.db_table.c.user_id == user_id).values(
                            lie=self.db_table.c.lie + 1))
                    elif self.db_row == "neurotism":
                        self.connection.execute(self.db_table.update(self.db_table.c.user_id == user_id).values(
                            neurotism=self.db_table.c.neurotism + 1))
                return 1
        self.api.messages.send(peer_id=user_id, random_id=get_random_id(), message="Извини, я тебя не понимаю!")
        return 0
