# Пользователь печатает в командной строке запрос,
# а наша задача состоит в том, чтобы найти координаты запрошенного объекта
# и показать его на карте, выбрав соответствующий масштаб и позицию карты

import pygame
import sys
import os
import requests

# Пусть наше приложение предполагает запуск в командной строке:
# python search_req.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:
# http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=Москва, ул. Ак. Королева, 12&format=json

API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'

# Функция сборки запроса для геокодера
def geocode(address):
    # Собираем запрос для геокодера.
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"}

    # Выполняем запрос.
    response = requests.get(geocoder_request, params=geocoder_params)

    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
    else:
        # прочитать о методах обработки ошибок, статусов ошибок
        pass

    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


# Получаем координаты объекта по его адресу.
def get_coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None, None
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Широта, долгота:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    ll = ",".join([toponym_longitude, toponym_lattitude])
    return ll


# Получаем параметры объекта для рисования карты вокруг него.
def get_ll_span(address):

    toponym = geocode(address)
    if not toponym:
        return (None, None)

    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и Широта :
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    # Собираем координаты в параметр ll
    ll = ",".join([toponym_longitude, toponym_lattitude])
    lowerCorner = toponym["boundedBy"]["Envelope"]["lowerCorner"].split()
    upperCorner = toponym["boundedBy"]["Envelope"]["upperCorner"].split()
    l = abs(float(lowerCorner[0]) - float(upperCorner[0]))
    r = abs(float(lowerCorner[1]) - float(upperCorner[1]))
    return ll, [r, l]


def show_map(ll_spn=None, map_type="map", add_params=None):
    if ll_spn:
        map_request = f"http://static-maps.yandex.ru/1.x/?{ll_spn}&l={map_type}"
    else:
        map_request = f"http://static-maps.yandex.ru/1.x/?l={map_type}"

    if add_params:
        map_request += "&" + add_params
    response = requests.get(map_request)

    if not response:
        pass

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    # Рисуем картинку, загружаемую из только что созданного файла.
    screen.blit(pygame.image.load(map_file), (0, 0))
    # Переключаем экран и ждем закрытия окна.
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass
    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(map_file)


def main():
    toponym_to_find = " ".join(sys.argv[1:-2])
    spn = sys.argv[-2:]
    if toponym_to_find:
        ll = get_coordinates(toponym_to_find)
        ll_spn = f"ll={ll}&spn={spn[0]},{spn[1]}"
        show_map(ll_spn, "map")


if __name__ == "__main__":
    main()
