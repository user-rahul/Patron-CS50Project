import requests
from app import request
from json import loads
import os
from geopy.geocoders import Nominatim
from cs50 import SQL
from flask import redirect


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


# Find the lat and long with the path
def path(origin, destination):

    # Convert the location to longitude and latitude (GEOPY)
    geolocator = Nominatim(user_agent="helpers.py")

    startLoc = geolocator.geocode(origin)
    endLoc = geolocator.geocode(destination)

    if startLoc is None or endLoc is None:
        return -1

    start_latitude = startLoc.latitude
    start_longitude = startLoc.longitude

    end_latitude = endLoc.latitude
    end_longitude = endLoc.longitude


    # OPEN ROUTE SERVICE
    headers = { 'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8', }

    API_KEY = os.environ.get("API_KEY")


    call = requests.get(f'https://api.openrouteservice.org/v2/directions/driving-car?api_key={API_KEY}&start={start_longitude}, {start_latitude}&end={end_longitude},{end_latitude}', headers=headers)


    if call.status_code != 200:
        return -1

    # Convert the string format of the json to the dict
    dict_geojson = loads(call.text)

    # Get the values of the key - coordinates
    coordinates = dict_geojson['features'][0]['geometry']['coordinates']

    # Return the coordinates
    return coordinates






def check():
    CONN = db.execute('SELECT ask.askuserid, helpers.helperuserid FROM ask,helpers WHERE ask.geo IN (SELECT helpers.geo FROM helpers)')
    return CONN