from flask import Flask
from flask import jsonify
from flask_cors import CORS, cross_origin
from skyfield.api import load

app = Flask(__name__)
CORS(app)


@app.route('/')
def fetch_satellites():
    satellites_file = load_satellites()
    current_time = compute_time()
    raw_fetch = compute_position(satellites_file, current_time)

    fetch = jsonify(raw_fetch)
    return fetch


def load_satellites():
    starlink_url = 'https://celestrak.com/NORAD/elements/starlink.txt'
    satellites = load.tle_file(starlink_url)
    return satellites


def compute_time():
    ts = load.timescale()
    time = ts.now()
    return time


def compute_position(satellites, time):
    results = []
    earth_radius = 6378100.0

    for satellite in satellites:
        # Geocentric
        geometry = satellite.at(time)

        # Geographic point beneath satellite

        subpoint = geometry.subpoint()
        latitude = subpoint.latitude
        longitude = subpoint.longitude
        elevation = subpoint.elevation

        adjusted_elevation = elevation.m / earth_radius

        results.append(latitude.degrees)
        results.append(longitude.degrees)
        results.append(adjusted_elevation)
        results.append(0)
    return results
