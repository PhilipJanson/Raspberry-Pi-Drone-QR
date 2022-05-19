import math
import requests
import argparse
from sense_hat import SenseHat
import cv2

sense = SenseHat()


def detectQrCode(qr):
    # set up camera object
    cap = cv2.VideoCapture(0)

    # QR code detection object
    detector = cv2.QRCodeDetector()

    while True:
        # get the image
        _, img = cap.read()
        # get bounding box coords and data
        data, bbox, _ = detector.detectAndDecode(img)

        # if there is a bounding box, draw one, along with the data
        if(bbox is not None):
            for i in range(len(bbox)):
                cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255,
                         0, 255), thickness=2)
            cv2.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)
            if data:
                print("data found: ", data)
                cap.release()
                cv2.destroyAllWindows()
                break

    return True


def getMovement(src, dst):
    speed = 0.00003
    dst_x, dst_y = dst
    x, y = src
    direction = math.sqrt((dst_x - x)**2 + (dst_y - y)**2)
    longitude_move = speed * ((dst_x - x) / direction)
    latitude_move = speed * ((dst_y - y) / direction)
    return longitude_move, latitude_move


def moveDrone(src, d_long, d_la):
    x, y = src
    x = x + d_long
    y = y + d_la
    return (x, y)


def send_location(SERVER_URL, id, drone_coords, status, userid, orderid, finished):
    if(status == 'idle'):
        sense.show_letter("I", (0, 255, 0))
    elif(status == 'busy'):
        sense.show_letter("B", (255, 0, 0))
    elif(status == 'waiting'):
        sense.show_letter("W", (255, 230, 30))

    with requests.Session() as session:
        drone_info = {'id': id,
                      'longitude': drone_coords[0],
                      'latitude': drone_coords[1],
                      'status': status,
                      'userid': userid,
                      'orderid': orderid,
                      'finished': finished
                      }
        resp = session.post(SERVER_URL, json=drone_info)


def distance(_fr, _to):
    _dist = ((_to[0] - _fr[0])**2 + (_to[1] - _fr[1])**2)*10**6
    return _dist


def run(id, current_coords, from_coords, to_coords, username, qr, userid, orderid, SERVER_URL):
    drone_coords = current_coords

    # Move from current_coodrs to from_coords
    d_long, d_la = getMovement(drone_coords, from_coords)
    while distance(drone_coords, from_coords) > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        send_location(SERVER_URL, id=id,
                      drone_coords=drone_coords, status='busy', userid=userid, orderid=orderid, finished=False)

    send_location(SERVER_URL, id=id,
                  drone_coords=drone_coords, status='waiting', userid=userid, orderid=orderid, finished=False)

    loop = True
    while(loop):
        for event in sense.stick.get_events():
            print(event.action)
            if event.action == "pressed" and event.direction == "up":
                loop = False

    # Move from from_coodrs to to_coords
    d_long, d_la = getMovement(drone_coords, to_coords)
    while distance(drone_coords, to_coords) > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        send_location(SERVER_URL, id=id,
                      drone_coords=drone_coords, status='busy', userid=userid, orderid=orderid, finished=False)

    sense.show_message("Hej " + username + "!")
    sense.show_message("Scanna din QR-kod")

    # Stop and update status to database
    send_location(SERVER_URL, id=id, drone_coords=drone_coords,
                  status='waiting', userid=userid, orderid=orderid, finished=False)
    finished = detectQrCode(qr)
    send_location(SERVER_URL, id=id, drone_coords=drone_coords,
                  status='idle', userid=userid, orderid=orderid, finished=finished)

    return drone_coords[0], drone_coords[1]


if __name__ == "__main__":
    SERVER_URL = "http://192.168.1.5:5001/drone"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--clong", help='current longitude of drone location', type=float)
    parser.add_argument(
        "--clat", help='current latitude of drone location', type=float)
    parser.add_argument(
        "--flong", help='longitude of input [from address]', type=float)
    parser.add_argument(
        "--flat", help='latitude of input [from address]', type=float)
    parser.add_argument(
        "--tlong", help='longitude of input [to address]', type=float)
    parser.add_argument(
        "--tlat", help='latitude of input [to address]', type=float)
    parser.add_argument("--id", help='drones ID', type=str)
    parser.add_argument("--user", help='username', type=str)
    parser.add_argument("--qr", help='qr code', type=str)
    parser.add_argument("--userid", help='users ID', type=str)
    parser.add_argument("--orderid", help='order ID', type=str)
    args = parser.parse_args()

    current_coords = (args.clong, args.clat)
    from_coords = (args.flong, args.flat)
    to_coords = (args.tlong, args.tlat)
    username = args.user
    qr = args.qr
    userid = args.userid
    orderid = args.orderid

    print("Get New Task!")

    drone_long, drone_lat = run(
        args.id, current_coords, from_coords, to_coords, username, qr, userid, orderid, SERVER_URL)

    file = open("coords.txt", "w")
    temp = str(drone_long) + "\n" + str(drone_lat) + "\n"
    file.writelines(temp)
    file.close()
