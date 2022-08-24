# Курсовой проект «Резервное копирование»
# первого блока «Основы языка программирования Python»

import module_vk
import module_ya
import module_service
from module_config import backup_params

CONFIG_FILE = 'module_config.py'

if __name__ == '__main__':
    print()
    print('Данная программа скопирует все новые фото с Вашего профиля ВК')
    print('и добавит их в корень вашего Я.Диска, в отдельную папку')
    print('-------------------------------------------------------------')
    module_service.my_timeout()

    # Проверяем наличие токена и user_id ВК в настроечноем файле
    # если не находим, то запрашиваем у пользователя и записываем в config.py
    module_vk.check_for_token('ВКонтакте')

    # Запрашиваем токен Яндекс, проверяем его и записываем в словарь
    module_vk.check_for_token('Яндекс.Диск')

    # # Выгружаем параметры работы из файла настроек в словарь
    # module_service.get_config_parameters(CONFIG_FILE)
    # exit()

    # Получаем список фотографий с ВК
    module_vk.get_vk_photos()

    # Формируем список самых больших доступных фото
    module_service.get_max_size_photos()

    # Загружаем фото по url с ВК на локальный диск
    module_service.download_vk_photos_to_local_disk()

    # Создаем папку на Я.Диске для загрузки фото
    module_ya.create_folder_on_ya_disk()

    # Загрузить фото на Я.Диск пользователя
    module_ya.upload_vk_photos_to_yadisk()

    print(f'Список загруженных фото с размерами см. в файле '
          f'{backup_params["upload_result_json"]}')
    print('Работа программы завершена')
