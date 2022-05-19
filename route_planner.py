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


def send_request(drone_url, coords):
    with requests.Session() as session:
        resp = session.post(drone_url, json=coords)


@app.route('/planner', methods=['POST'])
def route_planner():
    Data = json.loads(request.data.decode())
    FromAddress = Data['faddr']
    ToAddress = Data['taddr']
    username = str(Data['user'])
    
    if not username:
        return "Något gick fel, försök igen"
    
    user = User.query.filter_by(username=username).first()
    from_location = geolocator.geocode(FromAddress + region, timeout=None)
    to_location = geolocator.geocode(ToAddress + region, timeout=None)

    if FromAddress == "" or from_location is None:
        message = 'Upphämtningsadressen är inte giltig'
        return message
    elif ToAddress == "" or to_location is None:
        message = 'Avlämningsadressen är inte giltig'
        return message
    else:
        order = Order(delivered=False, user_id=user.id)
        db.session.add(order)
        db.session.commit()
        qr = generate_qr(user, order)  

        data = {'from': (from_location.longitude, from_location.latitude),
                  'to': (to_location.longitude, to_location.latitude),
                  'username': username,
                  'qr': qr
                  }
            
        if(redis_server.get('drone1_status') == 'idle'):
            message = 'Beställning mottagen och en drönare är nu på väg.'
            DRONE_URL = 'http://' + redis_server.get('drone1_IP') + ':5000'
            send_request(DRONE_URL, data)
        else:
            message = 'Ingen drönare är tillgänglig just nu, försök igen senare.'

        return message


def generate_qr(user, order):
    import hashlib
    import qrcode
    #from PIL import Image
    
    hashed_user = hashlib.sha224(str(user.id).encode('utf-8')).hexdigest()
    hashed_order = hashlib.sha224(str(order.id).encode('utf-8')).hexdigest()
    res = (hashed_user + hashed_order)[len(hashed_user) - 8 : len(hashed_user) + 8]
    
    print(res)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(res)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    img.save("/home/pi/Raspberry-Pi-Drone-QR/webserver/static/qr/" + str(user.id) + "_" + str(order.id) + ".png")
    
    return res

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5002')
