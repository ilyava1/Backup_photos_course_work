# Данный файл используется для хранение параметров работы программы «Резервное копирование»
# Для чтения параметров используется разделитель '; ' - не используйте его при создании/редактировании параметров

# Файл для записи ответа ВК на вызов метода photo.get
vk_photos_json = {
    param_name: 'vk_photos_json',
    param_description: 'Файл для записи ответа ВК на вызов метода photo.get',
    param_body: 'vk_photos.json'
}

# Файл для хранения ссылок ВК на загрузку фото в максимальном разрешении
vk_max_size_photos_json = {
    param_name: 'vk_max_size_photos_json',
    param_description: 'Файл для хранения ссылок ВК для загрузки фото в максимальном разрешении'
    param_body: 'vk_max_size_photos.json'
}

# Файл для хранения результатов загрузки согласно условию Задания
upload_result_json = {
    param_name: 'upload_result_json',
    param_description: 'Файл для хранения результатов загрузки согласно условию Задания'
    param_body: 'upload_result.json'
}

# Адрес директории на локальном диске для сохранения фотографий
dir_for_vk_photos = {
    param_name: 'dir_for_vk_photos',
    param_description: 'Адрес директории на локальном диске для сохранения фотографий',
    param_body: 'C:/Unic_VK_photos/'
}

# Адрес директории на Яндекс-диске для загрузки фотографий
yadisk_filepath = {
    param_name: 'yadisk_filepath',
    param_description: 'Адрес директории на Яндекс-диске для загрузки фотографий',
    param_body: 'Unic_VK_photos/'
}

# Макс кол-во фото для сохранения на Я.Диск
# Согласно условию Задания (Обязательные требования, п.3
photo_quantity = {
    param_name: 'photo_quantity',
    param_description: 'Макс кол-во фото для сохранения на Я.Диск',
    param_body: 5
}
