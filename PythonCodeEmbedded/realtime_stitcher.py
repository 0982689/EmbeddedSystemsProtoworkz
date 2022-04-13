# import the necessary packages
from __future__ import print_function
# from pyimagesearch.basicmotiondetector import BasicMotionDetector
from panorama import Stitcher
from imutils.video import VideoStream
import numpy as np
import datetime
import imutils
import time
import paho.mqtt.client as mqtt
import cv2 as cv

import people_detection as PD
PD = PD.PeopleDetection()
MQTT_ADDRESS = "77.161.23.64"
MQTT_USER = "proto"
MQTT_PASSWORD = "workz"
MQTT_TOPIC = "temperature"

tot = []

stitcher = Stitcher()
# motion = BasicMotionDetector(minArea=500)
# total = 0


def normalize(x):
    return ((float(x) - 20) / (40 - 20)) * 255


def on_connect(client, userdata, flags, rc):
    #  The callback for when the client receives a CONNACK response from the s>
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    print("Message received")
    t0 = time.time()
    #  The callback for when a PUBLISH message is received from the server."""

    msg.payload = msg.payload.decode("utf-8")
    msg.payload = msg.payload.split(",")
    msg.payload.pop()
    msg.payload = list(map(normalize, msg.payload))
    # print(msg.payload)
    # tot.extend(msg.payload)
    tot.append(msg.payload)
    if len(tot) == 2:
        pixel_array_reshape = np.reshape(tot[0], (24, 32))
        pixel_array = pixel_array_reshape.astype(np.uint8)
        im_color = cv.applyColorMap(pixel_array, cv.COLORMAP_JET)

        pixel_array_reshape1 = np.reshape(tot[1], (24, 32))
        pixel_array1 = pixel_array_reshape1.astype(np.uint8)
        im_color1 = cv.applyColorMap(pixel_array1, cv.COLORMAP_JET)

        # numpy_horizontal = np.hstack((im_color, im_color1))

        # PD.hsvThresh(numpy_horizontal)

        left = im_color
        right = im_color1
        result = stitcher.stitch([left, right])
        # no homograpy could be computed
        if result is None:
            print("[INFO] homography could not be computed")
        else:
            print("[INFO] homography computed successfully")
            gray = cv.cvtColor(result, cv.COLOR_BGR2GRAY)
            gray = cv.GaussianBlur(gray, (21, 21), 0)
            # increment the total number of frames read and draw the
            # timestamp on the image
            # total = total + 1
            # timestamp = datetime.datetime.now()
            # ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
            cv.putText(result, (10, result.shape[0] - 10),
                       cv.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            # show the output images
            cv.imshow("Result", result)
            cv.imwrite("./Filtering/result.jpg", result)
            cv.imshow("Left Frame", left)
            cv.imwrite("./Filtering/left.jpg", left)
            cv.imshow("Right Frame", right)
            cv.imwrite("./Filtering/right.jpg", right)
            key = cv.waitKey(1) & 0xFF
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                return
                # # cv.namedWindow("HeatMap", cv.WINDOW_NORMAL)
                # # cv.resizeWindow("HeatMap", 1280, 480)
                # # cv.imshow("HeatMap", numpy_horizontal)

                # cv.waitKey(1)

        tot.clear()

        # if cv.waitKey(33) == ord("q"):
        #     cv.destroyAllWindows()
        #     exit()
        t1 = time.time()

        print("Proces time: " + str(t1 - t0))


def main():

    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()


if __name__ == "__main__":
    main()
