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
MQTT_ADDRESS = "global ip address"
MQTT_USER = "username"
MQTT_PASSWORD = "password"
MQTT_TOPIC = "temperature"

tot = []
q = Queue()

# number of cameras
numOfCams = 2

# Minimum and maximum temperature used for normalization
minTemp = 15
maxTemp = 40


def sortInputmsg(msg):  # sort input message
    msg.payload = msg.payload.decode("utf-8")  # decode message
    msg.payload = msg.payload.split(",")  # split message
    msg.payload.pop()  # remove last element
    msg.payload = list(map(normalize, msg.payload))  # normalize temperature
    tot.append(msg.payload)  # add to total array


def reshapeCam(i):  # rehape input array to a image with heatmap
    pixel_array_reshape = np.reshape(tot[i], (24, 32))  # reshape array
    pixel_array_stitch = pixel_array_reshape.astype(
        np.uint8)  # convert to uint8
    im_color = cv.applyColorMap(
        pixel_array_stitch, cv.COLORMAP_JET)  # apply color map
    return im_color


def normalize(x):  # normalize temperature
    return ((float(x) - minTemp) / (maxTemp - minTemp)) * 255


def on_connect(client, userdata, flags, rc):  # The callback for when the client receives a CONNACK response from the server."""
    print("Connected with result code " +
          str(rc))  # Print result of connection
    client.subscribe(MQTT_TOPIC)  # Subscribe to our topic


def on_message(client, userdata, msg):
    t0 = time.time()
    #  The callback for when a PUBLISH message is received from the server."""
    sortInputmsg(msg)
    if len(tot) == numOfCams:  # if all cameras have been received
        im_color = reshapeCam(0)
        im_color1 = reshapeCam(1)

        # horizontal stack of matrixes
        numpy_horizontal = np.hstack((im_color, im_color1))

        PD.hsvThresh(numpy_horizontal)  # call hsvThresh function
        data = ((rnd.randint(6, 9), 2), (18, 16))  # random data
        #data = PD.get_coords()
        if PD.get_coords() is not None:  # if there is a person
            q.put(PD.get_coords())  # put coordinates in queue
        else:  # if there is no person
            print("none")  # print none

        # Could be uncommented for debugging
        # cv.namedWindow("HeatMap", cv.WINDOW_NORMAL)
        # cv.resizeWindow("HeatMap", 1280, 480)
        # cv.imshow("HeatMap", numpy_horizontal)

        # cv.waitKey(1)

        tot.clear()

        if cv.waitKey(33) == ord("q"):  # press q to quit
            cv.destroyAllWindows()  # destroy all windows
            exit()  # exit program
        t1 = time.time()

        print("Proces time: " + str(t1 - t0))  # print process time


# define the main function


def main():  # main function
    t1 = Thread(target=loop_mqtt, args=())  # create thread for mqtt
    t2 = Thread(target=loop_main, args=())  # create thread for main
    t1.start()  # start thread
    t2.start()  # start thread


def loop_main():  # main loop
    pass
    # APP.start(q)


def loop_mqtt():  # mqtt loop
    mqtt_client = mqtt.Client()  # create mqtt client
    # set username and password
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect  # set on connect function
    mqtt_client.on_message = on_message  # set on message function
    mqtt_client.connect(MQTT_ADDRESS, 1883)  # connect to mqtt server
    mqtt_client.loop_forever()  # loop forever


if __name__ == "__main__":  # if main
    main()  # call main function
