import cv2



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
                if data == qr:
                    print("qr-code valid")
                    sense.show_message("Valid qr-code", scroll_speed=0.06, text_colour=green)
                    cap.release()
                    cv2.destroyAllWindows()
                    return True
                else:
                    print("qr-code invalid")
                    sense.show_message("Invalid qr-code :(", scroll_speed=0.06, text_colour=red)
                    return False
                    
        cv2.imshow("code detector", img)
        
    # free camera object and exit
    cap.release()
    cv2.destroyAllWindows()
    
detectQrCode('aap')
