from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from sqlalchemy import *
from database import User

questions = [
    "Начнем наш диалог?",
    "Привет! Хочешь пообщаться, а заодно и внести свой вклад в науку?:)",
    "Ты любишь цветы?"
]
POSITIVE_BUTTON = ("Да", "positive")
NEGATIVE_BUTTON = ("Нет", "negative")
BACK_BUTTON = ("Назад", "default")


class StagesProvider:
    session = None
    api = None
    stages = None
    flag = 0

    def get_stages(self):
        stages = [StageWithKeyboard(self, questions[0], POSITIVE_BUTTON, NEGATIVE_BUTTON),
                  StageWithKeyboard(self, questions[1], POSITIVE_BUTTON, NEGATIVE_BUTTON)]
        with open("data/questions.txt", encoding='UTF-8') as file:
            for line in file.readlines():
                quest, row, value = line.split("|")
                stages.append(StageWithKeyboardAizenk(self, quest, value, row))
        self.stages = stages

    def __init__(self, session, api):
        self.session = session
        self.api = api
        return

    def get_instance(self):
        if not self.flag:
            self.get_stages()
            self.flag = 1
        return self.stages


class DefaultStage:
    text = None
    api = None

    def __init__(self, stage_provider, text, *args):
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

    def __init__(self, stage_provider, text, *args):
        super().__init__(stage_provider, text, *args)
        self.text = text
        self.api = stage_provider.api
        self.set_keyboard(args)
        self.buttons = args

    def send(self, user_id):
        self.api.messages.send(peer_id=user_id, random_id=get_random_id(), keyboard=self.keyboard.get_keyboard(),
                               message=self.text)

    def process(self, code, user_id, answer):
        if not code:
            self.send(user_id)
            return 0
        for button in self.buttons:
            if button[0] == answer.capitalize():
                if button[1] == 'negative':
                    return 0
                elif button[1] == 'positive':
                    return 1
        self.api.messages.send(peer_id=user_id, random_id=get_random_id(), message="Извини, я тебя не понимаю!")
        return 0


class StageWithKeyboardAizenk(StageWithKeyboard):
    session = None
    value = None
    parameter = None
    api = None
    stages = None

    def __init__(self, stages_provider, text, value, parameter):
        super().__init__(stages_provider, text, POSITIVE_BUTTON, NEGATIVE_BUTTON, BACK_BUTTON)
        self.session = stages_provider.session
        self.value = value
        self.api = stages_provider.api
        self.parameter = parameter
        self.stages = stages_provider.stages

    def process(self, code, user_id, answer):
        if not code:
            self.send(user_id)
            return 0
        if answer == "Назад":
            return -7
        for button in self.buttons:
            if button[0] == answer.capitalize():
                user = self.session.query(User).filter_by(id=user_id).first()
                if (button[1] == 'negative' and int(self.value) == -1) or (
                        button[1] == 'positive' and int(self.value) == 1):
                    setattr(user, self.parameter, getattr(user, self.parameter) + 1)
                    user.results += "+"
                else:
                    user.results += "-"
                self.session.commit()
                return 1
        self.api.messages.send(peer_id=user_id, random_id=get_random_id(), message="Извини, я тебя не понимаю!")
        return 0
