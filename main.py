# Курсовой проект «Резервное копирование»
# первого блока «Основы языка программирования Python»

import json
import time
import requests
from pprint import pprint
from datetime import datetime
import os

# Файл конфигурации (зависимостей) согласно условию Задания
# "Обязательные требования к программе" п.7
CONFIG_FILE = 'requiremеnts.txt'


# ____________________________________________________________________________
# Функции для работы с ВК

def check_for_token(service_name: str, token_name: str):
    """
    Функция проверки наличия токена.

    Функция получает на вход название сервиса, для которого требуется
    проверить токен, и имя токена (идентификатор токена в файле конфигурации),
    затем производит поиск токена в файле конфигурации. Если токена в файле
    конфигурации нет, функция запрашивает токен у пользователя. Введенный
    пользователем токен проверяется путем вызова функии обращения к веб-
    сервису за информации о пользователе. Если обращение прошло успешно,
    токен записывается в файл конфигурации и возвращается как результат
    работы функции.

    :param service_name: наименование веб-сервиса, для которого будет
    проверен токен.
    :param token_name: имя токена (идентификатор токена) в файле настроек
    :return: токен для работы с веб-сервисом
    """

    # Пытаемся читать файл настроек построчно, при нахождении имени токена
    # информируем об этом пользователя и возвращаем токен как результат
    # работы функции
    try:
        with open(CONFIG_FILE, 'rt', encoding='utf-8') as config:
            settings = config.readline()
            found_token = 0
            found_vk_user_id = 0
            vk_user_id = ''
            while settings:
                try:
                    cf_param_name, cf_param_text, cf_param_body = (
                        settings.split('; '))
                except:
                    settings = config.readline()
                    continue

                if cf_param_name == token_name:
                    token_user = cf_param_text
                    token_body = cf_param_body
                    print(f'Для загрузки файлов c {service_name} будет '
                          f'использован токен пользователя {token_user}')
                    found_token = 1
                    my_timeout()
                if service_name == 'ВКонтакте' and (
                        cf_param_name == 'vk_user_id'):
                    vk_user_id = cf_param_body
                    found_vk_user_id = 1

                settings = config.readline()

    except FileNotFoundError:
        print('Не найден настроечный файл')
        my_timeout()

    if service_name == 'ВКонтакте' and found_token == 1 and (
            found_vk_user_id == 1):
        return(token_body, vk_user_id)
    elif service_name == 'Яндекс.Диск' and found_token == 1:
        return (token_body)

    print(f'Неудачная попытка считать токен и/или user_id {service_name} '
          f'из настроечного файла')
    my_timeout()

    # Если настроечный файл не найден или в нем нет нужного токена, функция
    # запрашивает токен у пользователя и проверяет его через вызов функции
    # получения информации о пользователе от веб-сервиса
    param_error = 1
    while param_error == 1:
        if found_token == 0:
            token_body = input(f'Введите Ваш токен {service_name}: ')
        if service_name == 'ВКонтакте' and found_vk_user_id == 0:
            vk_user_id = input(f'Введите Ваш user_id {service_name}: ')

        print('Подождите, идет проверка ...')
        my_timeout()
        if service_name == 'ВКонтакте':
            service_response_error, token_user, service_response = (
                get_vk_user_info(token_body, vk_user_id))
        else:
            service_response_error, token_user, service_response = (
                get_ya_user_info(token_body))

        if service_response_error == 1:
            print('Введены неверные токен и/или user_id')
            print(f'Сообщение сервиса {service_name}:')
            pprint(service_response)
            print()
            continue
        else:
            with open(CONFIG_FILE, 'a', encoding='utf-8') as config:
                if service_name == 'ВКонтакте':
                    config.writelines('\n')
                    config.writelines('# ВК-токен \n')
                    config.writelines(f'{token_name}; {token_user}; '
                                      f'{token_body}\n')
                    config.writelines('# ВК-id_user \n')
                    config.writelines(f'"vk_user_id"; "ID пользователя ВК"; '
                                      f'{vk_user_id}\n')
                else:
                    config.writelines('\n')
                    config.writelines('# Яндекс-токен \n')
                    config.writelines(f'{token_name}; {token_user}; '
                                      f'{token_body}\n')

            if service_name == 'ВКонтакте':
                print(f'{token_user}, токен и user_id {service_name} '
                      f'успешно проверены и сохранены в файле настроек')
                print()
                return (token_body, vk_user_id)
            elif service_name == 'Яндекс.Диск':
                print(f'{token_user}, токен {service_name} '
                      f'успешно проверен и сохранен в файле настроек')
                print()
                return (token_body)


def get_vk_user_info(vk_token, vk_user_id):
    """
    Функция получения информации о пользователе ВКонтакте.

    Функция получает на вход токен ВКонтакте и обращается с ним
    за информацией о пользователе данного токена. Если ответ не
    содержит ошибку, то из него извлекается никнэйм пользователя,
    а если данное поля пустое - Имя и Фамилия пользователя

    :param vk_token: Токен ВК
    :return: Флаг ошибки - 0 или 1, юзер - никнэйм или И+Ф,
    json c ответом сервиса
    """
    user_info_url = "https://api.vk.com/method/users.get"
    params = {
        'access_token': vk_token,
        'user_ids': vk_user_id,
        'v': '5.131',
        'fields': ['nickname']
    }
    try:
        response = requests.get(user_info_url, params=params)
    except ValueError:
        vk_response_error = 1
        user = ''
        return (vk_response_error, user, response.json())

    if 'response' in response.json().keys():
        vk_response_error = 0
        if response.json()['response'][0]['nickname'] != '':
            user = response.json()['response'][0]['nickname'].capitalize()
        else:
            user = (response.json()['response'][0]['first_name']
                    .capitalize() + ' ' + response.json()['response']
                    [0]['last_name'].capitalize())
        service_response = response.status_code
        return (vk_response_error, user, service_response)
    else:
        vk_response_error = 1
        user = ''
        service_response = ('error_code: ' + str(response.json()['error']
                            ['error_code']) + '; error_msg: '
                            + response.json()['error']['error_msg'])
        return (vk_response_error, user, service_response)


def write_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def get_vk_photos(vk_token, vk_user_id, vk_photos_json):
    """
    Функция получения списка фотографий с ВК.

    Функция получает список фотографий с ВК с учетом параметровЖ
    'album_id': 'profile' - получить фото с профиля пользователяЖ
    'extended': '1' - вернуть фото с доп. полями, среди которых нам
    требуется количество лайков
    'photo_sizes': '1' - возвращать доступные размеры фотографий
    Результатом работы функции является json-файл с ответом сервиса ВК.

    :param vk_token: токен ВК
    :param vk_user_id: идентификатор пользователя ВК
    :param vk_photos_json: имя json-файла
    :return: json-файл с ответом сервиса ВК
    """
    base_url = 'https://api.vk.com/method/photos.get'
    params = {
        'access_token': vk_token,
        'owner_id': vk_user_id,
        'album_id': 'profile',
        'extended': '1',
        'photo_sizes': '1',
        'v': '5.131'
    }
    print('Идет обращение к ВК за списком фотографий профиля...')
    my_timeout()

    try:
        response = requests.get(base_url, params)
    except NameError:
        print('Проблема коммуникации с сервером. Работа программы завершена')
        exit()

    if response.status_code == 200:
        write_json(vk_photos_json, response.json())
        print(f'Ответ сервиса получен, сохранен в файле {vk_photos_json}')
    else:
        print('Ответ сервиса:')
        pprint(response.json())
        print()
        print('Работа программы завершена')


# ____________________________________________________________________________
# Сервисные функции

def get_config_parameters(config_dict):
    """
    Функция чтения параметров работы программы из файла настроек в словарь

    :param config_dict: на вход подается пустой словарь
    :return: словарь с настройками программы. Если заполнены не все настройки
    пользователю будет выведено уведомление
    """
    config_dict['vk_photos_json'] = ''
    config_dict['vk_max_size_photos_json'] = ''
    config_dict['upload_result_json'] = ''
    config_dict['dir_for_vk_photos'] = ''
    config_dict['yadisk_filepath'] = ''
    config_dict['photo_quantity'] = '5'

    print(f'Попытка прочесть настроечный файл {CONFIG_FILE}')
    my_timeout()
    try:
        with open(CONFIG_FILE, 'rt', encoding='utf-8') as config:
            settings = config.readline()
            while settings:
                try:
                    (cf_parameter_name, cf_parameter_description,
                     cf_parameter_value) = settings.split('; ')
                except:
                    settings = config.readline()
                    continue

                if cf_parameter_name == 'vk_photos_json':
                    config_dict['vk_photos_json'] = (cf_parameter_value
                                                     .replace('\n', ''))
                    print(f'Считан параметр {cf_parameter_name}:\n'
                          f'{cf_parameter_description}\n'
                          f'{cf_parameter_value}', end='')
                    my_timeout()
                elif cf_parameter_name == 'vk_max_size_photos_json':
                    config_dict['vk_max_size_photos_json'] = (
                        cf_parameter_value.replace('\n', ''))
                    print(f'Считан параметр {cf_parameter_name}:\n'
                          f'{cf_parameter_description}\n'
                          f'{cf_parameter_value}', end='')
                    my_timeout()
                elif cf_parameter_name == 'upload_result_json':
                    config_dict['upload_result_json'] = (cf_parameter_value
                                                         .replace('\n', ''))
                    print(f'Считан параметр {cf_parameter_name}:\n'
                          f'{cf_parameter_description}\n'
                          f'{cf_parameter_value}', end='')
                    my_timeout()
                elif cf_parameter_name == 'dir_for_vk_photos':
                    config_dict['dir_for_vk_photos'] = (cf_parameter_value
                                                        .replace('\n', ''))
                    print(f'Считан параметр {cf_parameter_name}:\n'
                          f'{cf_parameter_description}\n'
                          f'{cf_parameter_value}', end='')
                    my_timeout()
                elif cf_parameter_name == 'yadisk_filepath':
                    config_dict['yadisk_filepath'] = (cf_parameter_value
                                                      .replace('\n', ''))
                    print(f'Считан параметр {cf_parameter_name}:\n'
                          f'{cf_parameter_description}\n'
                          f'{cf_parameter_value}', end='')
                    my_timeout()
                elif cf_parameter_name == 'photo_quantity':
                    config_dict['photo_quantity'] = (cf_parameter_value
                                                     .replace('\n', ''))
                    print(f'Считан параметр {cf_parameter_name}:\n'
                          f'{cf_parameter_description}\n'
                          f'{cf_parameter_value}', end='')
                    my_timeout()

                settings = config.readline()

    except FileNotFoundError:
        print(f'В папке проекта не найден настроечный файл '
              f'{CONFIG_FILE}')
        print('Работа программы завершена')
        exit()

    if '' in config_dict.values():
        for key, value in config_dict.items():
            if value == '':
                print(f'Параметр {key} не задан. '
                      f'Отредактируйте параметр в файле настроек '
                      f'{CONFIG_FILE} и перезапутите программу')
                exit()
    print('Чтение файла настроек успешно завершено')
    my_timeout()
    return(config_dict)


def get_max_size_photos(vk_photos_json, vk_max_size_photos_json):
    """
    Функция получения максимального размера фото.

    Функция получает на вход словарь со всеми размерами всех фото. По каждому
    фото функция выбирает фото наибольшего размера и записываем результат в
    файл.
    :param vk_photos_json: файл со всеми фото во всех размерах
    :param vk_max_size_photos_json: файл с единственным наибольшим размером
    по каждому фото
    :return: файл с единственным наибольшим размером
    по каждому фото
    """
    items = json.load(open(vk_photos_json))['response']['items']
    items_quantity = len(items)
    print(f'Получена информация о {items_quantity} фото, '
          f'данные записаны в файл {vk_photos_json}')
    my_timeout()
    max_size_photos = []
    likes = []
    for item in items:
        max_size = {}
        # Если колечество лайков уникально, то названием фото будет
        # количество лайков. Если не уникально, то количество лайков+дата
        if item['likes']['count'] not in likes:
            likes.append(item['likes']['count'])
            max_size['photo_name'] = str(item['likes']['count']) + '_likes'
        else:
            max_size['photo_name'] = (str(item['likes']['count']) + '_likes_'
                                      + str(datetime.fromtimestamp
                                            (item['date'])).replace(':', '-')
                                      .replace(' ', '_'))
        max_size['photo_height'] = 0
        max_size['photo_width'] = 0
        max_size['size'] = ''
        max_size['photo_url'] = ''
        sizes = item['sizes']
        for size in sizes:
            if size['height'] + size['width'] > (max_size['photo_height']
                                                 + max_size['photo_width']):
                max_size['photo_height'] = size['height']
                max_size['photo_width'] = size['width']
                max_size['size'] = size['type']
                max_size['photo_url'] = size['url']
        max_size_photos.append(max_size)

    write_json(vk_max_size_photos_json, max_size_photos)
    print(f'Получены ссылки на фото с самым большим разрешением, '
          f'записаны в файл {vk_max_size_photos_json}')
    my_timeout()
    return


def download_vk_photos_to_local_disk(vk_max_size_photos_json,
                                     dir_for_vk_photos, photo_quantity):
    """
    Функция загрузки фото по URL на локальный диск.

    Функция получает на вход файл с перечнем фото для скачивания по URL.
    Каждое фото скачивается на локальный диск в папку, указанную в файле
    настроек.
    :param vk_max_size_photos_json: файл с перечнем фото и url для загрузки
    :param dir_for_vk_photos: папка на локальном диске для загрузки фото
    :param photo_quantity: максимальное количество фото для загрузки на диск
    :return: None
    """
    max_size_photos = json.load(open(vk_max_size_photos_json))
    try:
        os.mkdir(dir_for_vk_photos)
    except FileExistsError:
        print(f'Папка для записи фотографий на локальный диск '
              f'{dir_for_vk_photos} уже существует')
    else:
        print(f'Создана папка для записи фотографий на локальный диск '
              f'{dir_for_vk_photos}')
    my_timeout()

    # Проходим по словарю max_size_photo с сохраненными максимальными
    # размерами фото и загружаем каждое фото на локальный диск
    print(f'Начата загрузка фото на локальный диск в папку '
          f'{dir_for_vk_photos}')
    print(f'Согласно параметрам настроек программы будет загружено не более'
          f' {photo_quantity} фото в порядке их получения от сервиса ВК')
    my_timeout()
    # Счетчик для количества загруженных фото (по условию задачи
    # по умолчанию - не более 5-ти.
    # Параметр photo_quantity задается в requirements.txt
    ph_quantity = 0
    for max_size_photo in max_size_photos:
        if ph_quantity == photo_quantity:
            break
        response = requests.get(max_size_photo['photo_url'], stream=True)
        if response.status_code == 200:
            with open((dir_for_vk_photos + max_size_photo['photo_name']
                       + '.jpg'), 'bw') as file:
                for chunk in response.iter_content(4096):
                    file.write(chunk)
                current_filename = max_size_photo['photo_name'] + '.jpg'
                print(f'Файл {current_filename} загружен')
            ph_quantity += 1

    print()
    print(f'{len(max_size_photos)} фото загружено на локальный диск в папку '
          f'{dir_for_vk_photos}')
    print()
    return


def my_timeout():
    print()
    time.sleep(1)


# ____________________________________________________________________________
# Функции для работы с Яндексом

def get_headers(ya_token):
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'OAuth {}'.format(ya_token)
    }


def get_ya_user_info(ya_token):
    """
    Функция получения информации о пользователе Яндекс.

    Функция получает на вход токен Яндекс и обращается с ним
    за информацией о пользователе данного токена. Если ответ не
    содержит ошибку, то из него извлекается имя пользователя

    :param ya_token: Токен Яндекс
    :return: Флаг ошибки - 0 или 1, имя пользователя,
    json c ответом сервиса
    """
    user_info_url = "https://cloud-api.yandex.net/v1/disk"
    headers = get_headers(ya_token)
    response = requests.get(user_info_url, headers=headers)
    if response.status_code == 200:
        ya_response_error = 0
        service_response = response.status_code
        return (ya_response_error, response.json()['user']['display_name']
                .capitalize(), service_response)
    else:
        ya_response_error = 1
        user = ''
        service_response = response.json()
        return (ya_response_error, user, service_response)


def create_folder_on_ya_disk(ya_token, yadisk_filepath):
    """
    Функция создания папки на Я.Диске

    Функция получает на вход название папки и создает ее на Я.Диске
    владельца токена. Если папка уже существует, пользователю будет
    дано соответствующее уведомление. Выплонение программы при этом
    будет продолжено.
    :param ya_token: Яндекс-токен
    :param yadisk_filepath: имя папки для создания на Диске
    :return: None
    """
    create_folder_url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = get_headers(ya_token)
    params = {'path': yadisk_filepath}
    response = requests.put(create_folder_url, headers=headers,
                            params=params)
    if response.status_code == 201:
        print(f'Папка {yadisk_filepath} создана на Я.Диск')
        print()
    elif response.status_code == 409:
        print(f'Папка {yadisk_filepath} уже существует на Я.Диске.')
        print()
    else:
        print("Ответ сервиса на запрос по созданию папки:")
        print(response.json())
        print()

    return


def get_upload_link(ya_token, disk_file_path):
    """
    Функция получения ссылки для загрузки файла на Яндекс.Диск

    :param ya_token: Яндекс-токен
    :param disk_file_path: куда загружать файл на Я.Диск
    :return: словарь с ответом Я.Диска на запрос
    """
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = get_headers(ya_token)
    params = {"path": disk_file_path, "overwrite": "true"}
    response = requests.get(upload_url, headers=headers, params=params)

    return (response.json())


def upload_vk_photos_to_yadisk(ya_token, yadisk_filepath,
                               vk_max_size_photos_json, dir_for_vk_photos,
                               upload_result_json):
    """
    Функция загрузки фото с локального диска на Яндекс.Диск

    Функция получает на вход адрес папки на яндекс.диске, куда следует
    загружать фото, адрес папки на локальном диске, откуда загружать фото,
    файл с названиями и размерами фото, название файла для записи результата
    загрузки и токен яндекса.
    Для каждого фото функция получает ссылку для загрузки, загружает файл с
    помощью полученной ссылки, записывает результат в файл.
    :param ya_token:
    :param yadisk_filepath:
    :param vk_max_size_photos_json:
    :param dir_for_vk_photos:
    :param upload_result_json:
    :return:
    """
    print(f'Начата загрузка файлов с локального диска на Я.Диск в папку '
          f'{yadisk_filepath}')
    my_timeout()
    # Список для записи результатов загрузки согласно Заданию
    # (Выходные данные, п. 1)
    upload_result = []
    max_size_photos = json.load(open(vk_max_size_photos_json))
    for photo in max_size_photos:
        # Словарь для записи результата загрузки по каждому фото
        result = {}
        disk_file_path = yadisk_filepath + photo['photo_name'] + '.jpg'
        print(f'Загрузка на диск файла {photo["photo_name"] + ".jpg"} начата')
        time.sleep(1)
        href = get_upload_link(ya_token, disk_file_path=disk_file_path
                               ).get('href', '')
        print('Ссылка для загрузки файла получена. Загрузка начата...')
        time.sleep(1)
        filename = dir_for_vk_photos + photo['photo_name'] + '.jpg'

        response = requests.put(href, data=open(filename, 'rb'))
        response.raise_for_status()
        if response.status_code == 201:
            print(f'Файл {filename} успешно загружен на Я.Диск')
            my_timeout()
            result['file_name'] = photo['photo_name'] + '.jpg'
            result['size'] = photo['size']
            upload_result.append(result)
        else:
            print(f'Файл {filename} не загружен на Я.Диск. '
                  f'Ответ сервиса:')
            pprint(response.json())

    write_json(upload_result_json, upload_result)
    return


if __name__ == '__main__':
    print()
    print('Данная программа скопирует все новые фото с Вашего профиля ВК')
    print('и добавит их в корень вашего Я.Диска, в отдельную папку')
    print('-------------------------------------------------------------')
    print()
    my_timeout()

    # Инициализируем словарь для считывания настроек из настроечного
    # файла (requirements.txt)
    config_dict = {}
    # Запрашиваем токен и  user_id ВК, проверяем его и записываем в словарь
    config_dict['vk_token'], config_dict['vk_user_id'] = check_for_token(
        'ВКонтакте', 'vk_token')

    # Запрашиваем токен Яндекс, проверяем его и записываем в словарь
    config_dict['ya_token'] = check_for_token('Яндекс.Диск',
                                              'ya_token').replace('\n', '')

    # Выгружаем параметры работы из файла настроек в словарь
    config_dict = get_config_parameters(config_dict)

    # Получаем список фотографий с ВК
    get_vk_photos(config_dict['vk_token'], config_dict['vk_user_id'],
                  config_dict['vk_photos_json'])

    # Формируем список самых больших доступных фото
    get_max_size_photos(config_dict['vk_photos_json'],
                        config_dict['vk_max_size_photos_json'])

    # Загружаем фото по url с ВК на локальный диск
    download_vk_photos_to_local_disk(config_dict['vk_max_size_photos_json'],
                                     config_dict['dir_for_vk_photos'],
                                     config_dict['photo_quantity'])

    # Создаем папку на Я.Диске для загрузки фото
    create_folder_on_ya_disk(config_dict['ya_token'],
                             config_dict['yadisk_filepath'])

    # Загрузить фото на Я.Диск пользователя
    upload_vk_photos_to_yadisk(config_dict['ya_token'],
                               config_dict['yadisk_filepath'],
                               config_dict['vk_max_size_photos_json'],
                               config_dict['dir_for_vk_photos'],
                               config_dict['upload_result_json'])

    print(f'Список загруженных фото с размерами см. в файле '
          f'{config_dict["upload_result_json"]}')
    print('Работа программы завершена')
