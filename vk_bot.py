from vk_api.utils import get_random_id
import vk_api
import cfg
import Vkinder_db
from vk_api.longpoll import VkLongPoll, VkEventType


class VkBot():

    def __init__(self, acces_token=None, token=None) -> None:
        if token == None:
            self.vk = vk_api.VkApi(acces_token = cfg.acces_token, token = cfg.token)
        else:
            self.vk = vk_api.VkApi(acces_token, token=token)

        self.longpoll = VkLongPoll(self.vk)
        self.steps_functions = {
            1: lambda id_user, message_text: self.set_city(id_user, message_text),
            2: lambda id_user, message_text: self.set_age(id_user, message_text),
            3: lambda id_user, message_text: self.set_gender(id_user, message_text),
            4: lambda id_user, message_text: self.set_family(id_user, message_text),
            5: lambda id_user, message_text: self.create_partners_list(id_user),
            6: lambda id_user, message_text: self.processing_step_6(id_user, message_text)
        }

    def get_long_pool(self) -> VkLongPoll:
        return self.longpoll

    def send_message(self, id_user, message_text):
        """
        Отправка сообщения пользователю
        Входные параметры:
        vk - Объект подключения к VkApi
        id_user - id пользователя
        message_text - текст отправляемого сообщения
        """
        self.vk.method('messages.send',
                       {'user_id': id_user,
                        'message': message_text,
                        'random_id': get_random_id()})

    def send_message_with_photos(self, id_user, message_text, attachments):
        """
        Отправка сообщения c фотографиями пользователю
        Входные параметры:
        vk - Объект подключения к VkApi
        id_user - id пользователя
        message_text - текст отправляемого сообщения
        attachments - массив приложений
        """

        attachments = ",".join(attachments)
        self.vk.method('messages.send',
                       {'user_id': id_user,
                        'message': message_text,
                        'random_id': get_random_id(),
                        'attachment': attachments})

    def find_city(self, input_city):
        cities = self.vk.method('database.getCities', {'q': input_city})
        output = ''
        if cities['count'] != 0:
            cities = cities['items']
            for city in cities:
                cid = city.get('id')
                title = city.get('title')
                area = city.get('area')
                region = city.get('region')
                country = city.get('country')
                title = "" if title == None else title
                area = "" if area == None else area
                region = "" if region == None else region
                country = "" if country == None else country
                output += f"{cid} {title} {area} {region} {country}\n"
            return output
        else:
            return None

    def get_city_by_id(self, cid):
        cities = self.vk.method('database.getCitiesById', {'city_ids': cid})
        cities = cities[0]
        return cities.get('title')

    def set_city(self, id_user, message: str):
        if message.isdigit():
            city = self.get_city_by_id(message)
            if city:
                Vkinder_db.update_user_city(id_user, message)
                Vkinder_db.update_user_position(id_user, 2)
                self.send_message(id_user,
                                  f"Для поиска установлен город {city}.\nВведите возраст для поиска.")
            else:
                self.send_message(id_user,
                                  "Нет города с таким id.")
        else:
            cities = self.find_city(message)
            if cities:
                self.send_message(id_user,
                                  f"Введите id города из списка:\n{cities}.")
            else:
                self.send_message(id_user,
                                  f"Ничего не найдено по запросу {message}.\nВведите название города")

    def set_age(self, id_user, message_text: str):
        if message_text.isdigit():
            Vkinder_db.update_user_age(id_user, message_text)
            Vkinder_db.update_user_position(id_user, 3)
            self.send_message(id_user,
                              f"Для поиска установлен возраст {message_text}.\nУкажите пол: [М]ужской или [Ж]енский.")
        else:
            self.send_message(id_user,
                              f"Вы ввели не число. Введите целое число лет.")

    def set_gender(self, id_user, message_text: str):
        gender = message_text[0].upper()
        if gender in ['Ж', 'F']:
            gender = 1
        elif gender in ['М', 'M']:
            gender = 2
        else:
            self.send_message(id_user,
                              f"Укажите пол: [М]ужской или [Ж]енский.")
            return -1
        Vkinder_db.update_user_gender(id_user, gender)
        Vkinder_db.update_user_position(id_user, 4)
        self.send_message(id_user,
                          f"""Для поиска установлен возраст {message_text}.
            Введите семейное положение:
            [1] Не женат (не замужем)
            [2] Встречается
            [3] Помолвлен(-а)
            [4] Женат (замужем)
            [5] Все сложно
            [6] В активном поиске
            [7] Влюблен(-а)
            [8] В гражданском браке""")

    def set_family(self, id_user, message_text: str):
        if len(message_text) == 1 and '1' <= message_text <= '8':
            Vkinder_db.update_user_family(id_user, message_text)
            Vkinder_db.update_user_position(id_user, 5)
            self.send_message(id_user,
                              "Для поиска введите [П]оиск")
        else:
            self.send_message(id_user,
                              """Введите семейное положение:
                              [1] Не женат (не замужем)
                              [2] Встречается
                              [3] Помолвлен(-а)
                              [4] Женат (замужем)
                              [5] Все сложно
                              [6] В активном поиске
                              [7] Влюблен(-а)
                              [8] В гражданском браке""")

    def create_partners_list(self, id_user):
        city, gender, age, family = Vkinder_db.get_user_settings(id_user)
        age_from = age - 2 if age > 20 else 18
        age_to = age + 2
        partners = self.vk.method('users.search',
                                  {'count': 1000,
                                   'city_id': city,
                                   'sex': gender,
                                   'status': family,
                                   'age_from': age_from,
                                   'age_to': age_to})
        partners = partners['items']
        for partner in partners:
            uid = partner['id']
            firstname = partner['first_name']
            lastname = partner['last_name']
            closed = partner['is_closed']
            if not closed:
                Vkinder_db.insert_partners([id_user, uid, firstname, lastname])
        Vkinder_db.update_user_position(id_user, 6)
        self.get_new_partner(id_user)

    def get_top_photos(self, user_id):
        photos = self.vk.method('photos.getAll',
                                {'owner_id': user_id,
                                 'extended': True})
        photos = photos['items']
        photos_list = []
        for photo in photos:
            photo_id = f"photo{user_id}_{photo['id']}"
            likes = photo['likes']['count']
            photos_list.append([photo_id, likes])
        photos_list = sorted(photos_list, key=lambda x: x[1], reverse=True)
        if len(photos_list) <= 3:
            return photos_list
        return photos_list[:3]

    def get_new_partner(self, id_user):
        partner = Vkinder_db.get_user_from_db(id_user)
        if partner:
            id_partner, firstname, lastname = partner
            Vkinder_db.delete_candidate(id_user, id_partner)
            message = f"""{firstname} {lastname}
            vk.com/id{id_partner}
            Чтобы изменить настройки поиска введите [И]зменить
            Чтобы найти нового человека введите любое сообщение"""
            photos = self.get_top_photos(id_partner)
            photos = [photo[0] for photo in photos]
            self.send_message_with_photos(id_user, message, photos)

    def processing_step_6(self, id_user, message_text):
        if message_text[0].upper() == "И":
            Vkinder_db.update_user_position(id_user, 1)
            Vkinder_db.delete_candidates(id_user)
            self.set_city(id_user, message_text)
        else:
            self.get_new_partner(id_user)

    def processing_message(self, id_user, message_text):
        number_position = Vkinder_db.take_position(id_user)
        self.steps_functions[number_position](id_user, message_text)
