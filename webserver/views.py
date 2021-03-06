from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from flask.json import jsonify
from flask_socketio import SocketIO, emit
from .models import Order
from . import db
import redis


views = Blueprint("views", __name__)
redis_server = redis.Redis(
    "localhost", decode_responses=True, charset="unicode_escape")


# Translate OSM coordinate (longitude, latitude) to SVG coordinates (x,y).
# Input coords_osm is a tuple (longitude, latitude).
def translate(coords_osm):
    x_osm_lim = (13.143390664, 13.257501336)
    y_osm_lim = (55.678138854000004, 55.734680845999996)

    x_svg_lim = (212.155699, 968.644301)
    y_svg_lim = (103.68, 768.96)

    x_osm = coords_osm[0]
    y_osm = coords_osm[1]

    x_ratio = (x_svg_lim[1] - x_svg_lim[0]) / (x_osm_lim[1] - x_osm_lim[0])
    y_ratio = (y_svg_lim[1] - y_svg_lim[0]) / (y_osm_lim[1] - y_osm_lim[0])
    x_svg = x_ratio * (x_osm - x_osm_lim[0]) + x_svg_lim[0]
    y_svg = y_ratio * (y_osm_lim[1] - y_osm) + y_svg_lim[0]

    return x_svg, y_svg


@views.route('/', methods=['GET'])
@login_required
def home():
    return render_template('index.html', user=current_user)


@views.route('/user')
@login_required
def userpage():
    return render_template('user.html', user=current_user)


@views.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    userid = data['userid']
    orderid = data['orderid']
    order = Order.query.get(int(orderid))

    if order:
        if order.user_id == int(userid):
            order.delivered = True
            db.session.commit()

    return jsonify({})


@views.route('/get_drones', methods=['GET'])
def get_drones():
    drone1_coords = translate((float(redis_server.get('drone1_longitude')), float(
        redis_server.get('drone1_latitude'))))

    drone_dict = {'drone1': {'longitude': drone1_coords[0], 'latitude': drone1_coords[1], 'status': redis_server.get('drone1_status')}}

    return jsonify(drone_dict)
