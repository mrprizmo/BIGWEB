# Пользователь печатает в командной строке запрос,
# а наша задача состоит в том, чтобы найти координаты запрошенного объекта
# и показать его на карте, выбрав соответствующий масштаб и позицию карты

import pygame
import sys
import os
import requests

# Пусть наше приложение предполагает запуск в командной строке:
# python 1.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:
# http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=Москва, ул. Ак. Королева, 12&format=json

API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'
pygame.init()

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
    return [float(toponym_longitude), float(toponym_lattitude)]


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


def show_map(toponym_to_find, spn, map_type="map", add_params=None):
    map_file = "map.png"
    map_types = ['map', 'sat', 'sat,skl']
    map_type = map_type
    running = True
    shift = [0, 0]
    K_pressed = True
    while running:
        ll = get_coordinates(toponym_to_find)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    spn[0] += 0.001
                    spn[1] += 0.001
                elif event.key == pygame.K_PAGEDOWN:
                    spn[0] = max(0.0001, spn[0] - 0.001)
                    spn[1] = max(0.0001, spn[1] - 0.001)
                elif event.key == pygame.K_LEFT:
                    shift[0] -= 0.0001
                elif event.key == pygame.K_RIGHT:
                    shift[0] += 0.0001
                elif event.key == pygame.K_UP:
                    shift[1] += 0.0001
                elif event.key == pygame.K_DOWN:
                    shift[1] -= 0.0001
                elif event.key == pygame.K_SPACE:
                    map_type = map_types[(map_types.index(map_type) + 1) % 3]
                K_pressed = True
        if K_pressed:
            ll_spn = f"ll={','.join([str(ll[0] + shift[0]), str(ll[1] + shift[1])])}&spn={spn[0]},{spn[1]}"
            if ll_spn:
                map_request = f"http://static-maps.yandex.ru/1.x/?{ll_spn}&l={map_type}"
            else:
                map_request = f"http://static-maps.yandex.ru/1.x/?l={map_type}"

            if add_params:
                map_request += "&" + add_params
            response = requests.get(map_request)

            if not response:
                pass

            try:
                with open(map_file, "wb") as file:
                    file.write(response.content)
            except IOError as ex:
                print("Ошибка записи временного файла:", ex)
                sys.exit(2)

            K_pressed = False
            screen = pygame.display.set_mode((600, 450))
            screen.blit(pygame.image.load(map_file), (0, 0))
            pygame.display.flip()

    pygame.quit()
    os.remove(map_file)


def main():
    toponym_to_find = " ".join(sys.argv[1:-2])
    spn = list(map(float, sys.argv[-2:]))
    if toponym_to_find:
        show_map(toponym_to_find, spn, "map")


if __name__ == "__main__":
    main()
