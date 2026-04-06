import sys
import requests
from PIL import Image
from io import BytesIO
from distance import lonlat_distance
from map_params import get_map_params, get_map_params_two_points

GEOCODER_URL = "http://geocode-maps.yandex.ru/1.x/"
GEOCODER_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
SEARCH_URL = "https://search-maps.yandex.ru/v1/"
SEARCH_KEY = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
STATIC_URL = "https://static-maps.yandex.ru/v1"
STATIC_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"


def get_toponym(address):
    params = {
        "apikey": GEOCODER_KEY,
        "geocode": address,
        "format": "json",
    }
    response = requests.get(GEOCODER_URL, params=params)
    if not response:
        print("Ошибка геокодера:", response.status_code, response.reason)
        sys.exit(1)
    members = response.json()["response"]["GeoObjectCollection"]["featureMember"]
    if not members:
        print("Адрес не найден.")
        sys.exit(1)
    return members[0]["GeoObject"]


def get_coordinates(toponym):
    lon, lat = toponym["Point"]["pos"].split()
    return float(lon), float(lat)


def find_nearest_pharmacy(ll):
    params = {
        "apikey": SEARCH_KEY,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": f"{ll[0]},{ll[1]}",
        "type": "biz",
        "results": 1,
    }
    response = requests.get(SEARCH_URL, params=params)
    if not response:
        print("Ошибка поиска:", response.status_code, response.reason)
        sys.exit(1)
    features = response.json()["features"]
    if not features:
        print("Аптеки не найдены.")
        sys.exit(1)
    return features[0]


address = " ".join(sys.argv[1:])

toponym = get_toponym(address)
origin = get_coordinates(toponym)

pharmacy = find_nearest_pharmacy(origin)

meta = pharmacy["properties"]["CompanyMetaData"]
pharmacy_name = meta["name"]
pharmacy_address = meta["address"]
hours = meta.get("Hours", {}).get("text", "Время работы не указано")

ph_coords = pharmacy["geometry"]["coordinates"]
pharmacy_point = (ph_coords[0], ph_coords[1])

dist = lonlat_distance(origin, pharmacy_point)

print(f"Исходный адрес:  {address}")
print(f"Аптека:          {pharmacy_name}")
print(f"Адрес аптеки:    {pharmacy_address}")
print(f"Время работы:    {hours}")
print(f"Расстояние:      {dist:.0f} м ({dist / 1000:.2f} км)")

map_params = get_map_params_two_points(origin, pharmacy_point, STATIC_KEY)
map_params["pt"] = (
    f"{origin[0]},{origin[1]},pm2rdm~"
    f"{pharmacy_point[0]},{pharmacy_point[1]},pm2grm"
)

response = requests.get(STATIC_URL, params=map_params)
if not response:
    print("Ошибка StaticAPI:", response.status_code, response.reason)
    sys.exit(1)

image = Image.open(BytesIO(response.content))
image.show()
