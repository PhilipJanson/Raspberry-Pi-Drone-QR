from flask import Flask, request
from flask_cors import CORS
import redis

app = Flask(__name__)
CORS(app)
redis_server = redis.Redis(
    "localhost", decode_responses=True, charset="unicode_escape")


@app.route('/drone', methods=['POST'])
def drone():
    drone = request.get_json()
    droneIP = request.remote_addr
    droneID = drone['id']
    drone_longitude = drone['longitude']
    drone_latitude = drone['latitude']
    drone_status = drone['status']

    redis_server.set(droneID + '_IP', droneIP)
    redis_server.set(droneID + '_longitude', drone_longitude)
    redis_server.set(droneID + '_latitude', drone_latitude)
    redis_server.set(droneID + '_status', drone_status)

    return 'Get data'


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5001')
