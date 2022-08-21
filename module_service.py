# ____________________________________________________________________________
# Сервисные функции

from datetime import datetime
import requests
import time
import json
import os
from module_config import params


def write_json(filename, data):
    """
    Функция записи данных в json-файл.

    На вход функция получает имя файла и словарь данных.
    :param filename: имя файла для записи данных
    :param data: словарь с данными
    :return: None
    """
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def get_max_size_photos():
    """
    Функция получения максимального размера фото.

    Функция получает из параметров имя файла со всеми размерами всех фото. По каждому
    фото функция выбирает фото наибольшего размера и записываем результат в
    другой файл, имя которого также получено из параметров программы.

    :return: None
    """
    items = json.load(open(params[0]['param_body']))['response']['items']
    items_quantity = len(items)
    print(f'Получена информация о {items_quantity} фото, '
          f'данные записаны в файл {params[0]["param_body"]}')
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

    write_json(params[1]['param_body'], max_size_photos)
    print(f'Получены ссылки на фото с самым большим разрешением, '
          f'записаны в файл {params[1]["param_body"]}')
    my_timeout()
    return


def download_vk_photos_to_local_disk():
    """
    Функция загрузки фото по URL на локальный диск.

    Функция получает из параметров программы имя файла с перечнем фото для
    скачивания по URL. Каждое фото скачивается на локальный диск в папку,
    указанную в параметрах программы.

    :return: None
    """
    max_size_photos = json.load(open(params[1]['param_body']))
    try:
        os.mkdir(params[3]['param_body'])
    except FileExistsError:
        print(f'Папка для записи фотографий на локальный диск '
              f'{params[3]["param_body"]} уже существует')
    else:
        print(f'Создана папка для записи фотографий на локальный диск '
              f'{params[3]["param_body"]}')
    my_timeout()

    # Проходим по словарю max_size_photo с сохраненными максимальными
    # размерами фото и загружаем каждое фото на локальный диск
    print(f'Начата загрузка фото на локальный диск в папку '
          f'{params[3]["param_body"]}')
    print(f'Согласно параметрам настроек программы будет загружено не более'
          f' {params[5]["param_body"]} фото в порядке их получения от сервиса ВК')
    my_timeout()
    # Счетчик для количества загруженных фото (по условию задачи
    # по умолчанию - не более 5-ти.
    # Параметр photo_quantity задается в requirements.txt
    ph_quantity = 0
    for max_size_photo in max_size_photos:
        if ph_quantity == params[5]["param_body"]:
            break
        response = requests.get(max_size_photo['photo_url'], stream=True)
        if response.status_code == 200:
            with open((params[3]["param_body"] + max_size_photo['photo_name']
                       + '.jpg'), 'bw') as file:
                for chunk in response.iter_content(4096):
                    file.write(chunk)
                current_filename = max_size_photo['photo_name'] + '.jpg'
                print(f'Файл {current_filename} загружен')
            ph_quantity += 1

    print()
    print(f'{len(max_size_photos)} фото загружено на локальный диск в папку '
          f'{params[3]["param_body"]}')
    print()
    return


def my_timeout():
    print()
    time.sleep(1)
