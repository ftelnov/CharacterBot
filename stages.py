from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

questions = [
    "Начнем наш диалог?",
    "Привет! Хочешь пообщаться, а заодно и внести свой вклад в науку?:)",
    "Ты любишь цветы?"
]


def get_stages(api):
    stages = [
        Stage(api, 0, questions[0],
              ("Да", "positive"), ("Нет", "negative")),
        Stage(api, 1, questions[1],
              ("Да", "positive"), ("Нет", "negative")),
        Stage(api, 2, questions[2], ("Да", "positive"), ("Нет", "negative"))
    ]
    return stages


class Stage:
    num = None
    text = None
    keyboard = None
    api = None
    buttons = None
    users_received = None

    def set_keyboard(self, *args):
        self.keyboard = VkKeyboard(one_time=True)
        buttons = list(*args)
        for i in range(len(buttons)):
            button = buttons[i]
            self.keyboard.add_button(button[0], color=button[1])

    def __init__(self, api, num, text, *args):
        self.num = num
        self.text = text
        self.api = api
        self.set_keyboard(args)
        self.buttons = args
        self.users_received = dict()

    def send(self, user_id):
        self.api.messages.send(peer_id=user_id, random_id=get_random_id(), keyboard=self.keyboard.get_keyboard(),
                               message=self.text)

    def process(self, user_id, answer):
        if user_id not in self.users_received:
            self.users_received[user_id] = 1
            self.send(user_id)
            return 1
        for button in self.buttons:
            if button[0] == answer:
                if button[1] == 'negative':
                    self.api.messages.send(peer_id=user_id, random_id=get_random_id(),
                                           message="Очень жаль - пиши еще, если вдруг надумаешь!")
                    return -1
                else:
                    return 2
        self.api.messages.send(peer_id=user_id, random_id=get_random_id(), message="Извини, я тебя не понимаю!")
        return 0
