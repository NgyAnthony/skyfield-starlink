from flask import Flask
from flask import jsonify
from skyfield.api import load
from skyfield.iokit import parse_tle_file
from flask_cors import CORS
import urllib2
from contextlib import closing

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
    with closing(urllib2.urlopen(starlink_url)) as f:
        satellites = list(parse_tle_file(f))
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


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
