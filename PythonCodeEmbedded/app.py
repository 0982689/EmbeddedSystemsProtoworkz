from cgi import test
import tkinter as tk
from functools import partial
import numpy as np
import time

global active
active = None  # global variable to keep track of the active button


class View:  # the view class
    def __init__(self, root, q):  # constructor
        self.q = q  # queue
        self.root = root  # root
        self.array = []  # array to keep track of the buttons
        self.initialView()  # initial view

    def initialView(self):  # initial view
        self.root.attributes("-fullscreen", True)  # fullscreen

        canvas = tk.Canvas(self.root, width=1920, height=1080)  # canvas
        canvas.pack()  # pack

        canvas.create_text(750, 50, fill="black", font="Courier 14",
                           text="Fill in the measurements of your room.")  # text

        canvas.create_text(600, 100, fill="black",
                           font="Courier 10", text="Length:")  # text
        self.entry1 = tk.Entry(self.root)  # entry
        canvas.create_window(750, 100, window=self.entry1)  # window

        canvas.create_text(600, 125, fill="black",
                           font="Courier 10", text="Width:")  # text
        self.entry2 = tk.Entry(self.root)  # entry
        canvas.create_window(750, 125, window=self.entry2)  # window

        btn = tk.Button(canvas, text='Click for next screen.',
                        command=self.secondView)  # button
        btn.place(x=688, y=150)  # place
        canvas.pack()  # pack

    def secondView(self):  # second view
        self.var1 = float(self.entry1.get())  # get the length
        self.var2 = float(self.entry2.get())  # get the width

        self.root.destroy()  # destroy the root
        self.secondScreen = tk.Tk()  # create a new root

        self.secondScreen.attributes("-fullscreen", True)  # fullscreen

        canvas = tk.Canvas(self.secondScreen, width=1920,
                           height=1080)  # canvas
        canvas.pack()  # pack

        self.secondScreen.bind("<Key>", partial(self.keypress, canvas))  # bind

        canvas.create_rectangle(
            400, 50, 400 + self.var1 * 180, 50 + self.var2 * 180, outline='blue')  # rectangle
        self.sensor = canvas.create_rectangle(
            self.var1 * 180/2 + 395, self.var2 * 180/2 + 45, self.var1 * 180/2 + 405, self.var2 * 180/2 + 55, outline='red')  # rectangle
        canvas.pack()  # pack

        bedBtn = tk.Button(canvas, text='Bed',
                           command=partial(self.bedFunction, canvas))  # button
        bedBtn.place(x=50, y=50)  # place

        chairBtn = tk.Button(canvas, text='Chair',
                             command=partial(self.chairFunction, canvas))  # button
        chairBtn.place(x=50, y=100)  # place

        sofaBtn = tk.Button(canvas, text='Sofa',
                            command=partial(self.sofaFunction, canvas))  # button
        sofaBtn.place(x=50, y=150)  # place

        canvas.pack()  # pack

    def bedFunction(self, canvas):  # bed function
        bed = canvas.create_rectangle(
            400, 50, 580, 410, fill='red', activefill='cyan')  # rectangle
        listOfGlobals = globals()  # list of globals
        listOfGlobals['active'] = bed  # active
        self.array.append(bed)  # append
        canvas.tag_bind(bed, '<Double-1>',
                        partial(self.onClick, canvas))  # bind

    def chairFunction(self, canvas):  # chair function
        chair = canvas.create_rectangle(
            400, 50, 490, 140, fill='yellow', activefill='cyan')  # rectangle
        listOfGlobals = globals()  # list of globals
        listOfGlobals['active'] = chair  # active
        self.array.append(chair)  # append
        canvas.tag_bind(chair, '<Double-1>',
                        partial(self.onClick, canvas))  # bind

    def sofaFunction(self, canvas):  # sofa function
        sofa = canvas.create_rectangle(
            400, 50, 580, 320, fill='blue', activefill='cyan')  # rectangle
        listOfGlobals = globals()  # list of globals
        listOfGlobals['active'] = sofa  # active
        self.array.append(sofa)  # append
        canvas.tag_bind(sofa, '<Double-1>',
                        partial(self.onClick, canvas))  # bind

    def onClick(self, canvas, event):  # onClick
        listOfGlobals = globals()  # list of globals
        listOfGlobals['active'] = event.widget.find_closest(
            event.x, event.y)  # active

    def keypress(self, canvas, event):  # keypress
        x, y = 0, 0  # x, y
        if event.char == "a":  # if a
            x = -5
        elif event.char == "d":  # if d
            x = 5
        elif event.char == "w":  # if w
            y = -5
        elif event.char == "s":  # if s
            y = 5
        elif event.char == "c":  # if c
            self.calculatingCoords(canvas)  # calculate coordinates
        elif event.char == "f":  # if f
            self.updateScreen(canvas)  # update screen
        # this will produce an exception but can be ignored
        canvas.move(active, x, y)  # move

    def calculatingCoords(self, canvas):  # calculating coordinates
        sensor = canvas.coords(self.sensor)  # sensor
        coordSensor = [
            sensor[0] + (sensor[2] - sensor[0]), sensor[1] + (sensor[3] - sensor[1])]  # sensor
        sensorArray = []  # sensor array

        for item in self.array:  # for item in array
            corners = []  # corners

            coords = canvas.coords(item)  # coords

            tmpVar = ""  # tmp var
            x = coords[2] - coords[0]  # x
            y = coords[3] - coords[1]  # y

            if(x == 180 and y == 360):
                tmpVar = "Bed"
            elif(x == 90 and y == 90):
                tmpVar = "Chair"
            elif(x == 180 and y == 270):
                tmpVar = "Sofa"

            corners.append([coords[0], coords[1]])  # corners
            corners.append([coords[2], coords[1]])  # corners
            corners.append([coords[2], coords[3]])  # corners
            corners.append([coords[0], coords[3]])  # corners

            thisTuple = (tmpVar, corners)  # this tuple
            sensorArray.append(thisTuple)  # sensor array

        return sensorArray  # return sensor array

    def updateScreen(self, originalCanvas):  # update screen
        objects = self.calculatingCoords(originalCanvas)  # objects
        self.secondScreen.destroy()  # destroy

        self.update = tk.Tk()  # create a new root

        self.update.attributes("-fullscreen", True)  # fullscreen

        self.canvas = tk.Canvas(self.update, width=1920, height=1080)  # canvas
        self.canvas.pack()  # pack

        self.canvas.create_rectangle(
            400, 50, 400 + self.var1 * 180, 50 + self.var2 * 180, outline='black')  # rectangle
        sensor = self.canvas.create_rectangle(self.var1 * 180/2 + 395, self.var2 * 180 /
                                              2 + 45, self.var1 * 180/2 + 405, self.var2 * 180/2 + 55, outline='red')  # rectangle
        self.canvas.pack()  # pack

        for object in objects:  # for object in objects
            tempColor = ''  # temp color
            if object[0] == 'Bed':  # if bed
                tempColor = 'red'  # temp color
            elif object[0] == 'Chair':  # if chair
                tempColor = 'yellow'  # temp color
            elif object[0] == 'Sofa':  # if sofa
                tempColor = 'blue'  # temp color

            coordinates = object[1]  # coordinates
            corner0 = coordinates[0]  # corner0
            corner1 = coordinates[2]  # corner1
            self.canvas.create_rectangle(
                corner0[0], corner0[1], corner1[0], corner1[1], fill=tempColor)  # rectangle
# IndexError: invalid index to scalar variable.
        self.update.after(100, self.process_data)  # after 100

    def process_data(self):  # process data
        data = self.q.get()  # data
        self.personPlacing(data)  # person placing
        self.createWhiteBoxes()  # create white boxes
        self.update.after(100, self.process_data)  # after 100

    def personPlacing(self, data):  # person placing
        print("Person Placing")  # print
        self.canvas.delete('line')  # delete
        self.canvas.delete('whiteBox')  # delete
        coordinateLeftTop = data[0]  # coordinate left top
        print("left top: " + str(coordinateLeftTop))  # print
        coordinateRightBottom = data[1]  # coordinate right bottom
        # center off mass
        centerX = (
            coordinateLeftTop[0] + ((coordinateRightBottom[0] - coordinateLeftTop[0]) / 2))  # center x
        centerY = (
            coordinateLeftTop[1] + ((coordinateRightBottom[1] - coordinateLeftTop[1]) / 2))  # center y

        self.degrees(centerX)  # degrees
        self.degrees(coordinateLeftTop[0])  # degrees
        self.degrees(coordinateRightBottom[0])  # degrees

    def degrees(self, centerX):  # degrees
        heightToMiddle = 50 + self.var2 * 180 / 2  # height to middle
        point1 = [400 + self.var1 * 180/2, heightToMiddle]  # point1

        beta = np.radians(centerX * 3.4375)  # beta

        tmp = 0  # tmp
        if(np.degrees(beta) == 90):  # if 90
            point2 = [400 + self.var1 * 180/2, 50 + self.var2 * 180]  # point2
            self.canvas.create_line(
                point1[0], point1[1], point2[0], point2[1],  tag='line')  # line
            return
        elif(np.degrees(beta) == 270):  # if 270
            point2 = [400 + self.var1 * 180/2, 50]  # point2
            self.canvas.create_line(
                point1[0], point1[1], point2[0], point2[1], tag='line')  # line
            return
        elif(np.degrees(beta) < 90):  # if less than 90 degrees
            tmp = 270
            left = False
        elif(np.degrees(beta) < 180):  # if less than 180 degrees
            left = True
            tmp = 90
        elif(np.degrees(beta) < 270):  # if less than 270 degrees
            tmp = 90
            left = True
        elif(np.degrees(beta) < 360):  # if less than 360 degrees
            tmp = 270
            left = False

        alpha = np.radians(360 - tmp - np.degrees(beta))  # alpha

        width = self.var1 * 180  # width
        a = width / 2
        b = (a * np.sin(beta)) / np.sin(alpha)  # b

        # Drawing line c

        if(left):  # if left
            point2 = [400, 540 / 2 + b + 50]  # point2
        else:
            point2 = [400 + width, 540 / 2 + b + 50]  # point2

        self.canvas.create_line(point1[0], point1[1],
                                point2[0], point2[1], tag='line')  # line

    def createWhiteBoxes(self):  # create white boxes
        self.canvas.create_rectangle(
            0, 0, 400, 1080, fill='white', outline="", tags="whiteBox")  # rectangle
        self.canvas.create_rectangle(
            0, 0, 1920, 50, fill='white', outline="", tags="whiteBox")  # rectangle
        self.canvas.create_rectangle(401 + self.var1 * 180,
                                     0, 1920, 1080, fill='white', outline="", tags="whiteBox")  # rectangle
        self.canvas.create_rectangle(0, 51 + self.var2 * 180,
                                     1920, 1080, fill='white', outline="", tags="whiteBox")  # rectangle


def start(q):  # start
    root = tk.Tk()  # root
    view = View(root, q)  # view
    root.mainloop()  # mainloop
