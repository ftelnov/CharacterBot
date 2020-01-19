from charbot import CharBot
from time import sleep


def main():
    bot = CharBot()
    sleep(1.5)
    bot.init_longpol()
    sleep(1.5)
    bot.run()
    # longpoll = VkBotLongPoll(session, group_id)
    # for event in longpoll.listen():
    #     print(event)
    #     if event.type == VkBotEventType.MESSAGE_NEW:
    #
    #         body = event.object.message['text']
    #         current_id = event.object.message['from_id']
    #
    #         if current_id in they_writing:
    #             to = chatting[current_id][0]
    #             chatting[current_id].pop(0)
    #             they_writing.pop(0)
    #
    #             ide = api.messages.send(peer_id=current_id,
    #                                     message="Спасибо за помощь, если хочешь пообщаться еще, то напиши 'Начать'",
    #                                     random_id=get_random_id())
    #             ins = messages.insert().values(id=ide, from_id=current_id, destination_id=to, text=body)
    #             connection.execute(ins)
    #
    #         elif body == 'Начать':
    #             api.messages.send(peer_id=current_id,
    #                               message=privet,
    #                               random_id=get_random_id(), keyboard=yes_no.get_keyboard())
    #         elif body == 'Нет, не надо':
    #             api.messages.send(peer_id=current_id,
    #                               message="Ну ладно, но жди, тебе могут написать",
    #                               random_id=get_random_id(), keyboard=yes_no.get_keyboard())
    #         elif body == 'Да, я хочу общаться':
    #             list_users = api.groups.getMembers(group_id=160204503, fields='first_name', name_case='ins')["items"]
    #             human = choice(list_users)
    #             itr = 0
    #             no_talk = 0
    #             while 'deactivated' in human or human['id'] == current_id or \
    #                     (current_id in chatting and human['id'] in chatting[current_id]):
    #                 human = choice(list_users)
    #                 itr += 1
    #                 if itr > 2 * len(list_users):
    #                     no_talk = True
    #                     break
    #             if no_talk:
    #                 api.messages.send(peer_id=current_id,
    #                                   message="Не с кем поговорить, прости(",
    #                                   random_id=get_random_id())
    #             else:
    #                 api.messages.send(peer_id=current_id,
    #                                   message=greeting.format(human['last_name'], human["first_name"]),
    #                                   random_id=get_random_id())
    #                 if current_id not in chatting:
    #                     chatting[current_id] = list()
    #                 chatting[current_id].append(human['id'])
    #                 to_write.append([datetime.now(), current_id, human['id']])
    #         else:
    #             api.messages.send(peer_id=current_id,
    #                               message="Напиши 'Начать', чтобы найти собеседника",
    #                               random_id=get_random_id())
    #
    #     while len(to_write) > 0 and datetime.now() - to_write[0][0] > timedelta(seconds=2):  #
    #         info = api.users.get(user_id=to_write[0][2], name_case='ins')
    #         info = info[0]
    #         api.messages.send(peer_id=to_write[0][1],
    #                           message=after_3days.format(info['last_name'], info['first_name']),
    #                           random_id=get_random_id())
    #         they_writing.append(to_write[0][1])
    #         to_write.pop(0)


if __name__ == '__main__':
    main()
