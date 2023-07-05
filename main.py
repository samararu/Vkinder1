from vk_api.longpoll import VkEventType

import vk_bot

import threading

myBot = vk_bot.VkBot()
longpoll = myBot.get_long_pool()

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            print(request)
            threading.Thread(target=myBot.processing_message, args=(event.user_id, request)).start()
