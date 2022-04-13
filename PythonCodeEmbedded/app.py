from cgi import test
import tkinter as tk
from functools import partial
import numpy as np
import time

global active
active = None


class View:
    def __init__(self, root, q):
        self.q = q
        self.root = root
        self.array = []
        self.initialView()

    def initialView(self):
        self.root.attributes("-fullscreen", True)

        canvas = tk.Canvas(self.root, width=1920, height=1080)
        canvas.pack()

        canvas.create_text(750, 50, fill="black", font="Courier 14",
                           text="Fill in the measurements of your room.")

        canvas.create_text(600, 100, fill="black",
                           font="Courier 10", text="Length:")
        self.entry1 = tk.Entry(self.root)
        canvas.create_window(750, 100, window=self.entry1)

        canvas.create_text(600, 125, fill="black",
                           font="Courier 10", text="Width:")
        self.entry2 = tk.Entry(self.root)
        canvas.create_window(750, 125, window=self.entry2)

        btn = tk.Button(canvas, text='Click for next screen.',
                        command=self.secondView)
        btn.place(x=688, y=150)
        canvas.pack()

    def secondView(self):
        self.var1 = float(self.entry1.get())
        self.var2 = float(self.entry2.get())

        self.root.destroy()
        self.secondScreen = tk.Tk()

        self.secondScreen.attributes("-fullscreen", True)

        canvas = tk.Canvas(self.secondScreen, width=1920, height=1080)
        canvas.pack()

        self.secondScreen.bind("<Key>", partial(self.keypress, canvas))

        canvas.create_rectangle(
            400, 50, 400 + self.var1 * 180, 50 + self.var2 * 180, outline='blue')
        self.sensor = canvas.create_rectangle(
            self.var1 * 180/2 + 395, self.var2 * 180/2 + 45, self.var1 * 180/2 + 405, self.var2 * 180/2 + 55, outline='red')
        canvas.pack()

        bedBtn = tk.Button(canvas, text='Bed',
                           command=partial(self.bedFunction, canvas))
        bedBtn.place(x=50, y=50)

        chairBtn = tk.Button(canvas, text='Chair',
                             command=partial(self.chairFunction, canvas))
        chairBtn.place(x=50, y=100)

        sofaBtn = tk.Button(canvas, text='Sofa',
                            command=partial(self.sofaFunction, canvas))
        sofaBtn.place(x=50, y=150)

        canvas.pack()

    def bedFunction(self, canvas):
        bed = canvas.create_rectangle(
            400, 50, 580, 410, fill='red', activefill='cyan')
        listOfGlobals = globals()
        listOfGlobals['active'] = bed
        self.array.append(bed)
        canvas.tag_bind(bed, '<Double-1>', partial(self.onClick, canvas))

    def chairFunction(self, canvas):
        chair = canvas.create_rectangle(
            400, 50, 490, 140, fill='yellow', activefill='cyan')
        listOfGlobals = globals()
        listOfGlobals['active'] = chair
        self.array.append(chair)
        canvas.tag_bind(chair, '<Double-1>', partial(self.onClick, canvas))

    def sofaFunction(self, canvas):
        sofa = canvas.create_rectangle(
            400, 50, 580, 320, fill='blue', activefill='cyan')
        listOfGlobals = globals()
        listOfGlobals['active'] = sofa
        self.array.append(sofa)
        canvas.tag_bind(sofa, '<Double-1>', partial(self.onClick, canvas))

    def onClick(self, canvas, event):
        listOfGlobals = globals()
        listOfGlobals['active'] = event.widget.find_closest(event.x, event.y)

    def keypress(self, canvas, event):
        x, y = 0, 0
        if event.char == "a":
            x = -5
        elif event.char == "d":
            x = 5
        elif event.char == "w":
            y = -5
        elif event.char == "s":
            y = 5
        elif event.char == "c":
            self.calculatingCoords(canvas)
        elif event.char == "f":
            self.updateScreen(canvas)
        #canvas.move(active, x, y)

    def calculatingCoords(self, canvas):
        sensor = canvas.coords(self.sensor)
        coordSensor = [
            sensor[0] + (sensor[2] - sensor[0]), sensor[1] + (sensor[3] - sensor[1])]
        sensorArray = []
        corners = []

        for item in self.array:
            coords = canvas.coords(item)
            corners.clear()

            tmpVar = ""
            x = coords[2] - coords[0]
            y = coords[3] - coords[1]

            if(x == 180 and y == 360):
                tmpVar = "Bed"
            elif(x == 90 and y == 90):
                tmpVar = "Chair"
            elif(x == 180 and y == 270):
                tmpVar = "Sofa"

            corners.append([coords[0], coords[1]])
            corners.append([coords[2], coords[1]])
            corners.append([coords[2], coords[3]])
            corners.append([coords[0], coords[3]])

            temp = []
            temp.clear()
            for corner in corners:
                temp.append(np.degrees(
                    np.arctan((coordSensor[1] - corner[1]) / (coordSensor[0] - corner[0]))))

            thisTuple = (tmpVar, corners)
            sensorArray.append(thisTuple)
        return sensorArray

    def updateScreen(self, originalCanvas):
        objects = self.calculatingCoords(originalCanvas)
        self.secondScreen.destroy()

        self.update = tk.Tk()

        self.update.attributes("-fullscreen", True)

        self.canvas = tk.Canvas(self.update, width=1920, height=1080)
        self.canvas.pack()

        self.canvas.create_rectangle(
            400, 50, 400 + self.var1 * 180, 50 + self.var2 * 180, outline='black')
        sensor = self.canvas.create_rectangle(self.var1 * 180/2 + 395, self.var2 * 180 /
                                              2 + 45, self.var1 * 180/2 + 405, self.var2 * 180/2 + 55, outline='red')
        self.canvas.pack()

        for object in objects:
            tempColor = ''
            if object[0] == 'Bed':
                tempColor = 'red'
            elif object[0] == 'Chair':
                tempColor = 'yellow'
            elif object[0] == 'Sofa':
                tempColor = 'blue'

            coordinates = object[1]
            corner0 = coordinates[0]
            corner1 = coordinates[2]
            self.canvas.create_rectangle(
                corner0[0], corner0[1], corner1[0], corner1[1], fill=tempColor)

        self.update.after(100, self.process_data)

    def process_data(self):
        data = self.q.get()
        self.personPlacing(data)
        self.createWhiteBoxes()
        self.update.after(100, self.process_data)

    def personPlacing(self, data):
        print("Person Placing")
        self.canvas.delete('line')
        self.canvas.delete('whiteBox')
        coordinateLeftTop = data[0]
        coordinateRightBottom = data[1]
        # center off mass
        centerX = (
            coordinateLeftTop[0] + ((coordinateRightBottom[0] - coordinateLeftTop[0]) / 2))
        centerY = (
            coordinateLeftTop[1] + ((coordinateRightBottom[1] - coordinateLeftTop[1]) / 2))

        self.degrees(centerX)
        self.degrees(coordinateLeftTop[0])
        self.degrees(coordinateRightBottom[0])

    def degrees(self, centerX):
        heightToMiddle = 50 + self.var2 * 180 / 2
        point1 = [400 + self.var1 * 180/2, heightToMiddle]

        beta = np.radians(centerX * 3.4375)

        tmp = 0
        if(np.degrees(beta) == 90):
            point2 = [400 + self.var1 * 180/2, 50 + self.var2 * 180]
            self.canvas.create_line(
                point1[0], point1[1], point2[0], point2[1],  tag='line')
            return
        elif(np.degrees(beta) == 270):
            point2 = [400 + self.var1 * 180/2, 50]
            self.canvas.create_line(
                point1[0], point1[1], point2[0], point2[1], tag='line')
            return
        elif(np.degrees(beta) < 90):
            tmp = 270
            left = False
        elif(np.degrees(beta) < 180):
            left = True
            tmp = 90
        elif(np.degrees(beta) < 270):
            tmp = 90
            left = True
        elif(np.degrees(beta) < 360):
            tmp = 270
            left = False

        alpha = np.radians(360 - tmp - np.degrees(beta))

        width = self.var1 * 180
        a = width / 2
        b = (a * np.sin(beta)) / np.sin(alpha)

        # Drawing line c

        if(left):
            point2 = [400, 540 / 2 + b + 50]
        else:
            point2 = [400 + width, 540 / 2 + b + 50]

        self.canvas.create_line(point1[0], point1[1],
                                point2[0], point2[1], tag='line')

    def createWhiteBoxes(self):
        self.canvas.create_rectangle(
            0, 0, 400, 1080, fill='white', outline="", tags="whiteBox")
        self.canvas.create_rectangle(
            0, 0, 1920, 50, fill='white', outline="", tags="whiteBox")
        self.canvas.create_rectangle(401 + self.var1 * 180,
                                     0, 1920, 1080, fill='white', outline="", tags="whiteBox")
        self.canvas.create_rectangle(0, 51 + self.var2 * 180,
                                     1920, 1080, fill='white', outline="", tags="whiteBox")


def start(q):
    root = tk.Tk()
    view = View(root, q)
    root.mainloop()
