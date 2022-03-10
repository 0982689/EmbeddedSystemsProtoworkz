# Python program to convert list to image

# import required libraries
import numpy as np
import os
import cv2 as cv
import paho.mqtt.client as mqtt

MQTT_ADDRESS = '77.161.23.64'
MQTT_USER = 'proto'
MQTT_PASSWORD = 'workz'
MQTT_TOPIC = 'temperature'

def takePicture():
    num = len(os.listdir('../heatMaps'))
    cv.imwrite('../heatMaps/' + 'HeatMap_' + str(num) + '.png', im_color)
    print('Image: ' + '../heatMaps/' + 'HeatMap_' + str(num) + '.png ' + 'saved')

def on_connect(client, userdata, flags, rc):
#  The callback for when the client receives a CONNACK response from the s>
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)

def normalize(x):
    return ((float(x) - 20) / (40 - 20)) * 255
def on_message(client, userdata, msg):
#  The callback for when a PUBLISH message is received from the server."""

    # message = on_message()
    msg.payload = msg.payload.decode("utf-8")
    msg.payload = msg.payload.split(",")
    msg.payload.pop()
    msg.payload = list(map(normalize, msg.payload))
    print(type(msg.payload))
    print(msg.payload)
    print(type(msg.payload[0]))
    print(msg.payload[0])
    pixel_array = np.reshape(msg.payload, (24, 32))
    pixel_array = pixel_array.astype(np.uint8)
    im_color = cv.applyColorMap(pixel_array, cv.COLORMAP_JET)

    cv.namedWindow('HeatMap', cv.WINDOW_NORMAL)
    cv.resizeWindow('HeatMap', 1280, 960)
    cv.imshow('HeatMap', im_color)
    cv.waitKey(1)
    
    if cv.waitKey(33) == ord('k'):
        takePicture() 

    if cv.waitKey(33) == ord('q'):
        cv.destroyWindow('HeatMap')
if not (os.path.exists('../heatMaps')):
    os.makedirs('../heatMaps')


# define the main function
def main():
    
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()

if __name__ == "__main__":
    main()
