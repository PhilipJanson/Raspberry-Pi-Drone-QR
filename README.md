Drönarprojekt med QR-kodläsare

#####################################

Run Redis

redis-start

#####################################

Run webserver/database.py

export FLASK_APP=database.py
export FLASK_ENV=development
flask run --port=5001

#####################################

Run webserver/route_planner.py

export FLASK_APP=route_planner.py
export FLASK_ENV=development
flask run --port=5002

#####################################

Run build.py

export FLASK_APP=build.py
export FLASK_ENV=development
flask run

#####################################
