import os
import json
import requests
from geopy import distance
import folium
from flask import Flask
from dotenv import load_dotenv
import webbrowser


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def read_json():
    with open("coffee.json", "r", encoding="CP1251") as coffee_text:
        file_contents_json = coffee_text.read()
    file_contents = json.loads(file_contents_json)
    return file_contents


def fill_cafe_list(file_contents, longitude, latitude):
    cafe_list = []
    for i in range(len(file_contents)):
        cafe_dict = {
            "title": file_contents[i]['Name'],
            "distance": distance.distance(
                (latitude, longitude),
                [file_contents[i]['geoData']['coordinates'][1],
                 file_contents[i]['geoData']['coordinates'][0]]).km,
            "latitude": file_contents[i]['geoData']['coordinates'][1],
            "longitude": file_contents[i]['geoData']['coordinates'][0]
        }
        cafe_list.append(cafe_dict)
    return cafe_list


def get_cafe_distance(cafe):
    return cafe['distance']


def generate_html(cafe_list, longitude, latitude):
    five_close_cafe = (sorted(cafe_list, key=get_cafe_distance))[:5]
    m = folium.Map(location=[latitude, longitude], zoom_start=10)
    folium.Marker(
              location=[latitude, longitude],
              icon=folium.Icon(color='blue', icon="user", prefix='fa'),
          ).add_to(m)
    for i in five_close_cafe:
        folium.Marker(
            location=[i['latitude'], i['longitude']],
            popup=i['title'],
            icon=folium.Icon(color='red', icon="coffee", prefix='fa'),
        ).add_to(m)
    m.save("cafe.html")


def draw_coffee():
    with open('cafe.html') as file:
        return file.read()


def main():
    load_dotenv('secret.env')
    apikey = os.environ['APIKEY']
    longitude, latitude = fetch_coordinates(apikey, input("Где вы находитесь? "))
    file_contents = read_json()
    cafe_list = fill_cafe_list(file_contents, longitude, latitude)
    webbrowser.open_new_tab('http://127.0.0.1:5000')
    generate_html(cafe_list, longitude, latitude)
    app = Flask(__name__)
    app.add_url_rule('/', 'hello', draw_coffee)
    app.run('0.0.0.0')


if __name__ == '__main__':
    main()
