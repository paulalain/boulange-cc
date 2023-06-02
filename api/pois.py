import gpxpy
import gpxpy.gpx
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
from OSMPythonTools.nominatim import Nominatim
import math
import sys
import urllib.parse
from flask import jsonify

overpass = Overpass()
nominatim = Nominatim()

SKIP_POINTS = 50
RADIUS = 500 # meters
R_EARTH = 6378 * 1000 # meters
PI = 3.14159
MIN_KM_BEFORE_STOP = 10000 # meters

BAKERY = '"shop"="bakery"'
KEBAB = '"cuisine"="kebab"'
PIZZA = '"cuisine"="pizza"'
HISTORY = 'tourism="*"'
WATER = 'drinking_water="*"'
CAFE = '"amenity"="cafe"'

TYPE_BAKERY = "bakeries"
TYPE_CAFE = "cafes"
TYPE_KEBAB = "kebabs"
TYPE_PIZZA = "pizzas"
TYPE_HISTORY = "historical_points"
TYPE_WATER = "water_points"

def check_type(type):
    return type in [TYPE_BAKERY, TYPE_CAFE, TYPE_KEBAB, TYPE_PIZZA]


def get_selector(selector):
    if selector == TYPE_BAKERY:
        return BAKERY
    elif selector == TYPE_KEBAB:
        return KEBAB 
    elif selector == TYPE_PIZZA:
        return PIZZA
    elif selector == TYPE_HISTORY:
        return HISTORY
    elif selector == TYPE_WATER:
        return WATER
    elif selector == TYPE_CAFE:
        return CAFE

    return BAKERY

def get_box_for_coordinate(latitude, longitude):
    delta_latitude  = (RADIUS / R_EARTH) * (180 / PI)
    delta_longitude = (RADIUS / R_EARTH) * (180 / PI) / math.cos(latitude * PI/180)

    return [
            latitude - delta_latitude,
            longitude - delta_longitude,
            latitude + delta_latitude,
            longitude + delta_longitude
        ]

def get_city_name_from_coordinate(latitude, longitude):
    city = nominatim.query(latitude, longitude, reverse=True, zoom=10).address()
    if 'village' in city:
        return city['village']
    if 'town' in city:
        return city['town']
    if 'city' in city:
        return city['city']

    return ''


def get_poi_from_coordinate(latitude, longitude, selector):
    pois = dict()

    city = get_city_name_from_coordinate(latitude, longitude)
    query = overpassQueryBuilder(bbox=get_box_for_coordinate(latitude, longitude), elementType='node', selector=selector, includeGeometry=True)
    result = overpass.query(query)

    if result.nodes() is not None:
        for element in result.nodes():
            if element.tag('name') is not None:
                key = element.tag('name') + str(latitude) + str(longitude)
                poi = {
                    'name': element.tag('name'),
                    'hours': element.tag('opening_hours'),
                    'latitude': latitude,
                    'longitude': longitude,
                    'city': city
                }
                pois[element.tag('name')] = poi
    
    return pois

def add_in_dict(dict, pois, distance_from_start):
    for key in pois:
        if key not in dict:
            pois[key]['distance_from_start'] = distance_from_start / 1000
            dict[key] = pois[key]

def get_pois(poi_type, gpx_file):
    gpx = open(gpx_file, 'r')
    parsed_gpx = gpxpy.parse(gpx)

    pois = dict()
    i = 0

    for point_data in parsed_gpx.get_points_data():
        point, distance_from_start, track_no, segment_no, point_no = point_data
        if i % SKIP_POINTS == 0 and distance_from_start > 10000:
            add_in_dict(pois, get_poi_from_coordinate(point.latitude, point.longitude, get_selector(poi_type)), distance_from_start)
        i += 1

    return jsonify(pois)
