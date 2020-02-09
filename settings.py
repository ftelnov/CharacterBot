from os import environ

strings = {
    'token': environ.get("TOKEN"),
    'high_lie': "Вынужден Вам сообщить, что у вас наблюдается неискренность в ответах, что в свою очередь может "
                "свидетельствовать о демонстративном поведении. Пройти тест еще раз? ",
    'finished': "Извини, для тебя пока ничего нет, заглядывай позже!",
    'your_level_extro': "Ваш уровень экстраверсии/интроверсии: ",
    'your_level_neuro': "Ваш уровень стабильности психики: ",
    "need_renew": "Ваша ложь была замечена. Наберите слово 'Повторить', чтобы сбросить статистику.",
    "passed_to_chat": "Спасибо за участие. Теперь ты можешь початиться с анонимом. Напиши `Начать чат` или нажми на кнопку ниже.",
    "lets_start": "Сейчас ты увидишь несколько картин. Выбери ту из них, которая наиболее близка тебе по духу. Подумай хорошенько и напиши мне цифру, соответствующую этой картинке.",
    "teammate_end_conv": "Собеседник завершил чат. Прежде чем начать новый диалог, оцените эту беседу. Насколько она вам понравилась по шкале от 1 до 10?",
    "you_end_conv": "Вы завершили чат. Прежде чем начать новый диалог, оцените эту беседу. Насколько она вам понравилась по шкале от 1 до 10?"
}

ranges_extro = {
    (19, 30): "яркий экстраверт",
    (15, 19): "экстраверт",
    (12, 15): "склонность к экстраверсии",
    (11, 12): "среднее значение",
    (9, 12): "склонность к интроверсии",
    (5, 9): "интроверт",
    (-5, 5): "глубокий интроверт"
}

ranges_neuro = {
    (19, 30): "очень стабильная психика",
    (13, 19): "высоко стабильная психика",
    (9, 13): "средне стабильная психика",
    (-5, 9): "нестабильная психика"
}

grp_id = int(environ.get("GRP_ID"))
db_address = environ.get('BASE_ADDRESS')
