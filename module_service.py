# ____________________________________________________________________________
# Сервисные функции
from datetime import datetime
import requests
import time
import json
import os


def write_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def get_config_parameters(CONFIG_FILE, config_dict):
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

