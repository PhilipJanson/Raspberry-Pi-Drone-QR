from flask import Flask, request
from flask_cors import CORS
import subprocess
import  requests
import time

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

#Give a unique ID for the drone
#===================================================================
drone_id = "drone1"
#===================================================================

# Get initial longitude and latitude the drone
#===================================================================
current_longitude = 13.19571718319727
current_latitude = 55.70387870324643
#===================================================================

file = open("coords.txt", "w")
temp = str(current_longitude) + "\n" + str(current_latitude) + "\n"
file.writelines(temp)
file.close()

drone_info = {'id': drone_id,
                'longitude': current_longitude,
                'latitude': current_latitude,
                'status': 'idle'
            }

# Fill in the IP address of server, and send the initial location of the drone to the SERVER
#===================================================================
SERVER="http://192.168.1.5:5001/drone"
with requests.Session() as session:
    resp = session.post(SERVER, json=drone_info)
#===================================================================

@app.route('/', methods=['POST'])
def main():
    data = request.json
    file = open("coords.txt", "r")

    # Get current longitude and latitude of the drone 
    #===================================================================
    current_longitude = file.readline().strip()
    current_latitude = file.readline().strip()
    #===================================================================  

    from_coord = data['from']
    to_coord = data['to']
    username = data['username']
    qr = data['qr']
    subprocess.Popen(["python3", "simulator.py", '--clong', str(current_longitude), '--clat', str(current_latitude),
                                                 '--flong', str(from_coord[0]), '--flat', str(from_coord[1]),
                                                 '--tlong', str(to_coord[0]), '--tlat', str(to_coord[1]),
                                                 '--id', drone_id,
                                                 '--user', username,
                                                 '--qr', qr
                    ])
    return 'New route received'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
