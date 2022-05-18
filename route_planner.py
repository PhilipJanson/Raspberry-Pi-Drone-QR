from cmath import pi
from flask import Flask, request, render_template, jsonify
from flask.globals import current_app
from geopy.geocoders import Nominatim
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from webserver.models import User, Order
import redis
import json
import requests

db = SQLAlchemy()
DB_NAME = "webserver/database.db"

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


redis_server = redis.Redis(
    "localhost", decode_responses=True, charset="unicode_escape")
geolocator = Nominatim(user_agent="my_request")
region = ", Lund, Skåne, Sweden"

# Example to send coords as request to the drone


def send_request(drone_url, coords):
    with requests.Session() as session:
        resp = session.post(drone_url, json=coords)


@app.route('/planner', methods=['POST'])
def route_planner():
    Data = json.loads(request.data.decode())
    FromAddress = Data['faddr']
    ToAddress = Data['taddr']
    user = User.query.filter_by(username=str(Data['user'])).first()
    from_location = geolocator.geocode(FromAddress + region, timeout=None)
    to_location = geolocator.geocode(ToAddress + region, timeout=None)

    if from_location is None:
        message = 'Departure address not found, please input a correct address'
        return message
    elif to_location is None:
        message = 'Destination address not found, please input a correct address'
        return message
    else:
        order = Order(user_id=user.id)
        db.session.add(order)
        db.session.commit()
        qr = generate_qr(user, order)  

        data = {'from': (from_location.longitude, from_location.latitude),
                  'to': (to_location.longitude, to_location.latitude),
                  'qr': qr
                  }
            
        if(redis_server.get('drone1_status') == 'idle'):
            message = 'Got address and sent request to the drone'
            DRONE_URL = 'http://' + redis_server.get('drone1_IP') + ':5000'
            #send_request(DRONE_URL, data)
        elif(redis_server.get('drone2_status') == 'idle'):
            message = 'Got address and sent request to the drone'
            DRONE_URL = 'http://' + redis_server.get('drone2_IP') + ':5000'
            #send_request(DRONE_URL, data)
        else:
            message = 'No available drone, try later'

        return message


def generate_qr(user, order):
    print(user.id, order.id)
    
    #hash user.id
    #hash order.id
    
    #generate QR code
    #save image
    
    #return string
    
    return 0

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5002')