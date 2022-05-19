Drönarprojekt med QR-kodläsare

#####################################

Run Redis

redis-server

#####################################

Run main.py:

export FLASK_APP=main.py
export FLASK_ENV=development
flask run

#####################################

Run database/database.py:

export FLASK_APP=database.py
export FLASK_ENV=development
flask run --port=5001 --host 0.0.0.0

#####################################

Run route_planner.py:

export FLASK_APP=route_planner.py
export FLASK_ENV=development
flask run --port=5002

#####################################
