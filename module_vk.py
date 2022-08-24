# ____________________________________________________________________________
# Функции для работы с ВК

import json
import requests
import module_service
import module_ya
from module_config import backup_params
from pprint import pprint


def check_for_token(service_name: str):
    """
    Функция проверки наличия токена.

    Функция получает на вход название сервиса, для которого требуется
    проверить токен, и производит поиск токена в модуле конфигурации. Если
    токена нет,функция запрашивает токен у пользователя. Введенный
    пользователем токен проверяется путем вызова функии обращения к
    веб-сервису за информации о пользователе. Если обращение прошло успешно,
    токен записывается в параметры программы, модуль конфигурации.

    :param service_name: наименование веб-сервиса, для которого будет
    проверен токен.

    :return: None
    """

    # Пытаемся читать файл настроек построчно, при нахождении имени токена
    # информируем об этом пользователя и возвращаем токен как результат
    # работы функции

    flag_vk_token = 0
    flag_vk_user_id = 0
    flag_ya_token = 0

    if service_name == 'ВКонтакте' and 'vk_token' in backup_params.keys():
        print(f'Для загрузки файлов c {service_name} будет '
              f'использован токен пользователя {backup_params["vk_token_user"]}')
        flag_vk_token = 1
        print()

    if service_name == 'ВКонтакте' and 'vk_user_id' in backup_params.keys():
        print(f'Для загрузки файлов c {service_name} считан '
              f'{backup_params["vk_user_id_description"]}')
        flag_vk_user_id = 1
        print()

    if service_name == 'Яндекс.Диск' and 'ya_token' in backup_params.keys():
        print(f'Для загрузки файлов c {service_name} будет '
              f'использован токен пользователя {backup_params["ya_token_user"]}')
        flag_ya_token = 1
        print()

    if service_name == 'ВКонтакте':
        if flag_vk_token == 1 and flag_vk_user_id == 1:
            return
    else:
        if flag_ya_token == 1:
            return

    error = 1
    while error == 1:
        if service_name == 'ВКонтакте' and flag_vk_token == 0:
            vk_token = input(f'Введите Ваш токен {service_name}: ')

        if service_name == 'ВКонтакте'and flag_vk_user_id == 0:
            vk_user_id = input(f'Введите Ваш user_id {service_name}: ')

        if service_name == 'Яндекс.Диск' and flag_ya_token == 0:
            ya_token = input(f'Введите Ваш токен {service_name}: ')

        print('Подождите, идет проверка ...')
        module_service.my_timeout()
        if service_name == 'ВКонтакте':
            service_response_error, token_user, service_response = (
                get_vk_user_info(vk_token, vk_user_id))
        else:
            service_response_error, token_user, service_response = (
                module_ya.get_ya_user_info(ya_token))

        if service_response_error == 1:
            print('Введены неверные данные')
            print(f'Сообщение сервиса {service_name}:')
            pprint(service_response)
            print()
            continue
        else:
            if service_name == 'ВКонтакте' and flag_vk_token == 0:
                backup_params['vk_token'] = vk_token
                backup_params['vk_token_user'] = token_user
                flag_vk_token = 1

            if service_name == 'ВКонтакте' and flag_vk_user_id == 0:
                backup_params['vk_user_id'] = vk_user_id
                backup_params['vk_user_id_description'] = 'Идентификатор ' \
                                                            'пользователя ' \
                                                            'ВКонтакте'
                flag_vk_user_id = 1

            if service_name == 'Яндекс.Диск' and flag_ya_token == 0:
                backup_params['ya_token'] = ya_token
                backup_params['ya_token_user'] = token_user
                flag_ya_token = 1

        with open('module_config.py', 'w', encoding='utf-8') as config:
            config.writelines('backup_params = {\n')
            for key, value in backup_params.items():
                config.writelines(f'"{key}": "{value}",\n')
            config.writelines('}\n')

        error = 0

    if service_name == 'ВКонтакте':
        print(f'{token_user}, токен и user_id {service_name} '
              f'успешно проверены и сохранены в файле настроек')
        print()
        return
    elif service_name == 'Яндекс.Диск':
        print(f'{token_user}, токен {service_name} '
              f'успешно проверен и сохранен в файле настроек')
        print()
        return


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


def get_vk_photos():
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
    request_parameters = {
        'access_token': backup_params['vk_token'],
        'owner_id': backup_params['vk_user_id'],
        'album_id': 'profile',
        'extended': '1',
        'photo_sizes': '1',
        'v': '5.131'
    }
    print('Идет обращение к ВК за списком фотографий профиля...')
    module_service.my_timeout()

    try:
        response = requests.get(base_url, request_parameters)
    except NameError:
        print('Проблема коммуникации с сервером. Работа программы завершена')
        exit()

    if response.status_code == 200:
        module_service.write_json(backup_params['vk_photos_json'], response.json())
        print(f'Ответ сервиса получен, сохранен в файле {backup_params["vk_photos_json"]}')
    else:
        print('Ответ сервиса:')
        pprint(response.json())
        print()
        print('Работа программы завершена')
