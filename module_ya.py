# ____________________________________________________________________________
# Функции для работы с Яндексом

import json
import time
import requests
from pprint import pprint
import module_service
from module_config import params


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


def create_folder_on_ya_disk():
    """
    Функция создания папки на Я.Диске

    Функция пытается создать папку на Я.Диске, название папки извлекается
    из настроек. Если папка уже существует, пользователю будет дано
    соответствующее уведомление. Выплонение программы при этом будет
    продолжено.

    :return: None
    """
    create_folder_url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = get_headers(params[8]["param_body"])
    parameters = {'path': params[4]["param_body"]}
    response = requests.put(create_folder_url, headers=headers,
                            params=parameters)
    if response.status_code == 201:
        print(f'Папка {params[4]["param_body"]} создана на Я.Диск')
        print()
    elif response.status_code == 409:
        print(f'Папка {params[4]["param_body"]} уже существует на Я.Диске.')
        print()
    else:
        print("Ответ сервиса на запрос по созданию папки:")
        print(response.json())
        print()

    return


def get_upload_link(disk_file_path):
    """
    Функция получения ссылки для загрузки файла на Яндекс.Диск

    :param disk_file_path: куда загружать файл на Я.Диск
    :return: словарь с ответом Я.Диска на запрос
    """
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = get_headers(params[8]["param_body"])
    parameters = {"path": disk_file_path, "overwrite": "true"}
    response = requests.get(upload_url, headers=headers, params=parameters)

    return (response.json())


def upload_vk_photos_to_yadisk():
    """
    Функция загрузки фото с локального диска на Яндекс.Диск

    Для каждого фото функция получает ссылку для загрузки, загружает файл с
    помощью полученной ссылки и записывает результат в файл.

    :return: None
    """
    print(f'Начата загрузка файлов с локального диска на Я.Диск в папку '
          f'{params[4]["param_body"]}')
    module_service.my_timeout()
    # Список для записи результатов загрузки согласно Заданию
    # (Выходные данные, п. 1)
    upload_result = []
    max_size_photos = json.load(open(params[1]["param_body"]))
    for photo in max_size_photos:
        # Словарь для записи результата загрузки по каждому фото
        result = {}
        disk_file_path = params[4]["param_body"] + photo['photo_name'] + '.jpg'
        print(f'Загрузка на диск файла {photo["photo_name"] + ".jpg"} начата')
        time.sleep(1)
        href = get_upload_link(disk_file_path=disk_file_path
                               ).get('href', '')
        print('Ссылка для загрузки файла получена. Загрузка начата...')
        time.sleep(1)
        filename = params[3]["param_body"] + photo['photo_name'] + '.jpg'

        response = requests.put(href, data=open(filename, 'rb'))
        response.raise_for_status()
        if response.status_code == 201:
            print(f'Файл {filename} успешно загружен на Я.Диск')
            module_service.my_timeout()
            result['file_name'] = photo['photo_name'] + '.jpg'
            result['size'] = photo['size']
            upload_result.append(result)
        else:
            print(f'Файл {filename} не загружен на Я.Диск. '
                  f'Ответ сервиса:')
            pprint(response.json())

    module_service.write_json(params[2]["param_body"], upload_result)
    return
