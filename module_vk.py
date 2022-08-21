# ____________________________________________________________________________
# Функции для работы с ВК

import json
import requests
import service_module
import ya_module
from pprint import pprint


def check_for_token(CONFIG_FILE, service_name: str, token_name: str):
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
                    service_module.my_timeout()
                if service_name == 'ВКонтакте' and (
                        cf_param_name == 'vk_user_id'):
                    vk_user_id = cf_param_body
                    found_vk_user_id = 1

                settings = config.readline()

    except FileNotFoundError:
        print('Не найден настроечный файл')
        service_module.my_timeout()

    if service_name == 'ВКонтакте' and found_token == 1 and (
            found_vk_user_id == 1):
        return(token_body, vk_user_id)
    elif service_name == 'Яндекс.Диск' and found_token == 1:
        return (token_body)

    print(f'Неудачная попытка считать токен и/или user_id {service_name} '
          f'из настроечного файла')
    service_module.my_timeout()

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
        service_module.my_timeout()
        if service_name == 'ВКонтакте':
            service_response_error, token_user, service_response = (
                get_vk_user_info(token_body, vk_user_id))
        else:
            service_response_error, token_user, service_response = (
                ya_module.get_ya_user_info(token_body))

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
    service_module.my_timeout()

    try:
        response = requests.get(base_url, params)
    except NameError:
        print('Проблема коммуникации с сервером. Работа программы завершена')
        exit()

    if response.status_code == 200:
        service_module.write_json(vk_photos_json, response.json())
        print(f'Ответ сервиса получен, сохранен в файле {vk_photos_json}')
    else:
        print('Ответ сервиса:')
        pprint(response.json())
        print()
        print('Работа программы завершена')
