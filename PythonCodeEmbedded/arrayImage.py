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


def on_connect(client, userdata, flags, rc):
#  The callback for when the client receives a CONNACK response from the s>
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
#  The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    return msg.payload

if not (os.path.exists('../heatMaps')):
    os.makedirs('../heatMaps')


# define the main function
def main():
    
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)

    
    num = len(os.listdir('../heatMaps'))
    list_pix = [24.44, 25.94, 25.39, 25.30, 25.59, 26.05, 27.23, 28.59, 28.34, 26.92, 25.10, 24.76, 25.00, 25.21, 23.94,
                23.98, 23.41, 23.43, 23.64,
                23.12, 23.37, 23.50, 23.56, 23.30, 23.26, 23.53, 23.82, 23.71, 23.33, 23.66, 23.34, 23.67, 25.51, 26.53,
                25.07, 25.01, 25.60, 25.96, 27.94,
                28.42, 28.78, 27.09, 25.17, 24.87, 24.91, 24.99, 23.93, 23.91, 23.85, 23.36, 23.39, 23.45, 23.93, 23.54,
                23.14, 23.05, 23.42, 23.37, 23.48,
                23.33, 23.52, 23.56, 23.29, 23.87, 24.49, 24.77, 24.74, 24.77, 25.67, 26.16, 27.27, 27.94, 28.57, 27.74,
                24.98, 25.33, 24.88, 25.36, 23.95,
                24.02, 23.65, 23.49, 23.15, 23.18, 23.48, 23.48, 23.66, 24.24, 23.56, 23.73, 23.35, 23.98, 23.93, 23.86,
                23.31, 23.98, 24.75, 24.01, 24.69,
                24.14, 25.11, 25.01, 25.69, 26.12, 26.94, 26.69, 25.02, 24.87, 25.05, 24.83, 24.69, 24.27, 24.23, 23.42,
                23.02, 23.14, 23.07, 22.79, 24.17,
                25.33, 24.85, 24.18, 24.21, 23.92, 24.23, 24.20, 23.64, 23.57, 24.41, 24.21, 24.37, 23.98, 24.63, 24.95,
                25.79, 25.93, 25.48, 25.77, 25.30,
                25.00, 24.93, 26.04, 29.15, 29.71, 26.89, 25.16, 22.63, 22.84, 22.59, 22.60, 22.88, 23.64, 26.29, 26.52,
                24.66, 24.61, 23.96, 24.20, 23.49,
                23.78, 24.72, 24.56, 24.12, 24.36, 24.71, 24.96, 25.87, 25.98, 25.94, 25.45, 25.32, 25.09, 25.25, 26.00,
                30.59, 30.97, 27.93, 25.02, 22.66,
                22.84, 22.93, 22.93, 23.16, 22.69, 25.12, 26.28, 26.19, 25.22, 24.49, 24.24, 24.00, 23.67, 24.17, 24.21,
                24.26, 24.24, 24.40, 24.87, 25.21,
                25.35, 25.30, 25.32, 24.66, 24.95, 24.49, 24.95, 26.08, 26.78, 24.35, 23.29, 22.46, 22.44, 22.40, 22.90,
                23.43, 23.51, 23.19, 23.88, 26.91,
                27.35, 25.50, 24.95, 24.40, 24.53, 24.25, 23.86, 23.95, 24.11, 24.55, 24.49, 25.03, 25.27, 25.36, 24.94,
                24.94, 25.01, 24.96, 24.61, 23.86,
                23.53, 23.17, 22.52, 22.48, 22.66, 22.61, 22.64, 23.12, 23.19, 23.14, 23.13, 24.73, 26.72, 27.41, 25.36,
                24.62, 24.32, 24.19, 24.14, 24.19,
                24.37, 24.58, 24.65, 24.86, 25.10, 24.85, 25.41, 24.95, 25.45, 24.75, 24.12, 23.27, 22.97, 22.47, 22.70,
                22.61, 22.54, 22.26, 22.89, 22.63,
                23.12, 23.04, 23.34, 23.56, 23.97, 26.97, 27.62, 24.81, 24.61, 24.42, 24.14, 24.23, 24.50, 24.60, 24.91,
                25.14, 25.29, 26.00, 26.01, 25.29,
                25.38, 24.69, 23.92, 23.51, 23.10, 22.86, 22.93, 22.37, 22.50, 22.79, 22.82, 22.80, 22.97, 23.56, 23.55,
                23.71, 23.72, 24.76, 27.02, 26.01,
                24.35, 23.81, 24.10, 24.49, 24.13, 24.38, 24.70, 24.90, 25.63, 26.67, 26.34, 25.20, 25.43, 24.94, 24.13,
                23.39, 23.96, 22.91, 23.03, 22.85,
                23.42, 23.61, 23.84, 23.89, 24.00, 23.37, 23.51, 23.14, 23.53, 23.19, 23.72, 24.07, 24.02, 23.96, 24.04,
                23.71, 24.39, 24.56, 24.32, 25.04,
                25.14, 25.42, 25.48, 24.73, 25.10, 24.75, 23.82, 23.01, 24.17, 23.62, 23.50, 23.98, 24.21, 24.15, 24.06,
                23.50, 23.45, 23.27, 22.95, 23.03,
                23.10, 23.58, 23.25, 23.23, 23.15, 24.05, 24.12, 24.01, 24.20, 23.98, 24.58, 24.62, 24.71, 24.48, 25.02,
                24.21, 24.18, 24.25, 24.55, 24.51,
                25.20, 25.03, 24.84, 24.14, 23.96, 23.51, 23.67, 23.09, 23.06, 22.59, 22.81, 22.99, 23.12, 23.12, 23.32,
                22.61, 23.21, 24.01, 23.87, 24.15,
                23.85, 24.32, 24.58, 25.12, 24.83, 24.96, 24.98, 24.55, 24.59, 24.72, 25.00, 25.17, 25.29, 25.43, 24.42,
                23.92, 23.68, 23.34, 23.02, 23.10,
                22.87, 23.09, 22.95, 23.07, 23.01, 23.07, 22.98, 22.85, 23.26, 23.58, 24.36, 24.56, 25.09, 24.74, 25.42,
                25.63, 25.41, 24.98, 25.43, 24.75,
                24.90, 25.21, 25.37, 24.76, 24.49, 24.68, 24.50, 22.97, 22.98, 22.52, 23.29, 22.79, 23.14, 22.85, 22.91,
                22.74, 23.04, 22.57, 23.06, 22.64,
                23.03, 23.99, 23.87, 24.66, 24.75, 25.05, 25.19, 25.44, 25.54, 25.04, 25.23, 24.75, 25.07, 25.20, 25.09,
                24.32, 23.87, 23.98, 24.19, 22.86,
                22.83, 22.98, 22.74, 22.93, 22.91, 23.03, 22.68, 22.72, 22.76, 22.87, 22.74, 23.28, 23.49, 24.36, 24.42,
                24.56, 24.81, 25.13, 25.95, 25.48,
                25.09, 25.34, 25.46, 25.51, 25.38, 23.93, 23.67, 22.79, 22.88, 23.10, 23.80, 23.29, 23.01, 22.92, 23.10,
                22.70, 22.85, 22.81, 22.96, 22.66,
                22.99, 22.62, 23.55, 23.21, 23.16, 24.36, 24.04, 24.33, 24.06, 25.29, 25.55, 25.37, 25.16, 25.16, 25.22,
                25.21, 24.66, 23.19, 22.86, 22.66,
                22.78, 23.12, 23.33, 23.89, 23.29, 22.88, 22.89, 22.92, 22.88, 22.86, 23.01, 22.39, 22.46, 23.15, 22.98,
                23.23, 23.43, 24.07, 24.67, 24.60,
                24.51, 25.35, 25.79, 25.44, 25.12, 25.07, 24.92, 24.70, 23.75, 22.49, 22.56, 22.55, 22.67, 22.94, 23.24,
                24.59, 24.17, 22.90, 23.23, 22.87,
                22.93, 22.77, 22.86, 22.60, 22.78, 23.13, 22.98, 23.16, 23.29, 24.71, 23.96, 24.49, 24.79, 26.04, 26.01,
                26.29, 25.68, 26.15, 25.95, 24.77,
                23.76, 22.52, 22.33, 22.48, 22.51, 22.77, 22.84, 24.46, 24.60, 23.02, 23.19, 22.68, 22.56, 22.80, 22.40,
                22.70, 22.73, 22.93, 23.04, 22.78,
                23.58, 24.78, 25.06, 24.76, 25.73, 26.71, 26.81, 27.90, 28.70, 28.88, 28.22, 25.45, 24.32, 22.51, 22.46,
                22.04, 22.27, 22.72, 22.91, 23.50,
                23.99, 22.96, 23.18, 22.53, 22.80, 22.70, 22.92, 22.78, 22.86, 22.71, 22.99, 22.82, 23.67, 24.48, 24.63,
                24.92, 25.39, 26.89, 26.51, 28.23,
                28.99, 29.86, 29.13, 25.66, 24.12, 22.87, 22.25, 22.19, 22.47, 22.58, 22.75, 23.18, 23.34, 23.10, 23.10,
                22.90, 22.78, 22.91, 22.74, 23.22,
                22.75, 23.12, 23.11, 22.96, 23.63, 25.10, 25.79, 25.13, 25.44, 26.45, 26.85, 28.32, 29.00, 29.95, 29.72,
                26.46, 25.65, 23.43, 23.01, 22.34,
                22.83, 23.47, 23.74, 22.71, 23.05, 23.35, 22.89, 22.74, 22.64, 22.74, 23.04, 22.96, 23.03, 22.53, 23.15,
                22.70, 23.55, 24.96, 24.86, 25.86,
                25.54, 26.73, 27.05, 28.61, 28.68, 30.23, 30.03, 26.78, 26.02, 24.37, 23.63, 23.29, 24.16, 26.01, 25.08,
                23.04, 22.97, 23.81, 23.49, 22.75,
                23.13, 22.96, 22.83, 22.96, 22.78, 22.80, 22.95, 22.87, 23.46]

    pixel_array = np.reshape(list_pix, (32, 24))
    pixel_array = pixel_array.astype(np.uint8)
    im_color = cv.applyColorMap(pixel_array, cv.COLORMAP_JET)

    # Show datastream as heatmap real time
    cv.namedWindow('HeatMap', cv.WINDOW_NORMAL)
    cv.resizeWindow('HeatMap', 1280, 960)
    cv.imshow('HeatMap', im_color)
    cv.waitKey(0)
    
    if cv.waitKey(0) & 0xFF == ord('q'):
        cv.destroyAllWindows()

    cv.imwrite('../heatMaps/' + 'HeatMap_' + str(num) + '.png', im_color)
    print('Image: ' + '../heatMaps/' + 'HeatMap_' + str(num) + '.png ' + 'saved')

    mqtt_client.loop_forever()

if __name__ == "__main__":
    main()
