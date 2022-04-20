# import required libraries
import numpy as np
import os
import cv2 as cv
import paho.mqtt.client as mqtt
import time
import tkinter as tk
import multiprocessing as mp
from queue import Queue
from threading import Thread
# Import classes
import people_detection as PD
import app as APP
import random as rnd
PD = PD.PeopleDetection()
MQTT_ADDRESS = "77.161.23.64"
MQTT_USER = "proto"
MQTT_PASSWORD = "workz"
MQTT_TOPIC = "temperature"

tot = []
q = Queue()


def normalize(x):
    return ((float(x) - 15) / (40 - 15)) * 255


def on_connect(client, userdata, flags, rc):
    #  The callback for when the client receives a CONNACK response from the s>
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
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

        numpy_horizontal = np.hstack((im_color, im_color1))

        PD.hsvThresh(numpy_horizontal)
        data = ((rnd.randint(6, 9), 2), (18, 16))
        #data = PD.get_coords()
        if PD.get_coords() is not None:
            q.put(PD.get_coords())
        else:
            print("none")
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


# define the main function


def main():
    t1 = Thread(target=loop_mqtt, args=())
    t2 = Thread(target=loop_main, args=())
    t1.start()
    t2.start()


def loop_main():
    pass
    #APP.start(q)


def loop_mqtt():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()


if __name__ == "__main__":
    main()
