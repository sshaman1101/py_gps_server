from flask import Flask, request, jsonify
import models
import config

app = Flask(__name__)


def convert_coordinate(coord):
    degrees = float(coord[:2])
    min_sec = float(coord[2:]) / 60

    return degrees + min_sec


def write_to_log(data):
    with open(config.log_file, "a") as f:
        f.write("Recieved parameter: %s \r\n" % data)


def write_to_db(lat, lon, alt, speed):
    point = models.Point()
    point.lat = lat
    point.lon = lon
    point.alt = alt
    point.speed = speed
    point.save()


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/gps", methods=['GET', 'POST'])
def serve():
    lat_raw = request.args.get('latitude', '')
    if not lat_raw:
        lat_raw = request.args.get('lat', '')

    lon_raw = request.args.get('longitude', '')
    if not lon_raw:
        lon_raw = request.args.get('lon')

    alt_raw = request.args.get('altitude', '')
    if not alt_raw:
        alt_raw = request.args.get('alt', '0')

    speed_raw = request.args.get('speed', '0')


    if not lat_raw or not lon_raw:
        return jsonify({
            'error': 400,
            'message': 'Bad request. Provide lat-lon or latitude-longitude',
        })

    lat = convert_coordinate(lat_raw)
    lon = convert_coordinate(lon_raw)
    alt = float(alt_raw)
    speed = float(speed_raw)

    write_to_db(lat, lon, alt, speed)

    return jsonify({
        'error': 0,
        'lat': lat,
        'lon': lon,
        'alt': alt,
        'speed': speed
    })


@app.route('/list', methods=['GET', ])
def list():
    points = models.Point.select().order_by(models.Point.created_at.desc())
    data = [point.json for point in points]

    return jsonify({
        'points': data,
        'error': 0,
    })


if __name__ == '__main__':
    app.run(debug=True)
