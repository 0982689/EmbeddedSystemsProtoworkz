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
        self.initial_view()  # initial view

    def initial_view(self):  # initial view
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
        self.second_screen = tk.Tk()  # create a new root

        self.second_screen.attributes("-fullscreen", True)  # fullscreen

        canvas = tk.Canvas(self.second_screen, width=1920,
                           height=1080)  # canvas
        canvas.pack()  # pack

        self.second_screen.bind("<Key>", partial(
            self.keypress, canvas))  # bind

        canvas.create_rectangle(
            400, 50, 400 + self.var1 * 180, 50 + self.var2 * 180, outline='blue')  # rectangle
        self.sensor = canvas.create_rectangle(
            self.var1 * 180/2 + 395, self.var2 * 180/2 + 45, self.var1 * 180/2 + 405, self.var2 * 180/2 + 55, outline='red')  # rectangle
        canvas.pack()  # pack

        bed_btn = tk.Button(canvas, text='Bed',
                            command=partial(self.bed_function, canvas))  # button
        bed_btn.place(x=50, y=50)  # place

        chair_btn = tk.Button(canvas, text='Chair',
                              command=partial(self.chair_function, canvas))  # button
        chair_btn.place(x=50, y=100)  # place

        sofa_btn = tk.Button(canvas, text='Sofa',
                             command=partial(self.sofa_function, canvas))  # button
        sofa_btn.place(x=50, y=150)  # place

        canvas.pack()  # pack

    def bed_function(self, canvas):  # bed function
        bed = canvas.create_rectangle(
            400, 50, 580, 410, fill='red', activefill='cyan')  # rectangle
        list_of_globals = globals()  # list of globals
        list_of_globals['active'] = bed  # active
        self.array.append(bed)  # append
        canvas.tag_bind(bed, '<Double-1>',
                        partial(self.on_click, canvas))  # bind

    def chair_function(self, canvas):  # chair function
        chair = canvas.create_rectangle(
            400, 50, 490, 140, fill='yellow', activefill='cyan')  # rectangle
        list_of_globals = globals()  # list of globals
        list_of_globals['active'] = chair  # active
        self.array.append(chair)  # append
        canvas.tag_bind(chair, '<Double-1>',
                        partial(self.on_click, canvas))  # bind

    def sofa_function(self, canvas):  # sofa function
        sofa = canvas.create_rectangle(
            400, 50, 580, 320, fill='blue', activefill='cyan')  # rectangle
        list_of_globals = globals()  # list of globals
        list_of_globals['active'] = sofa  # active
        self.array.append(sofa)  # append
        canvas.tag_bind(sofa, '<Double-1>',
                        partial(self.on_click, canvas))  # bind

    def on_click(self, canvas, event):  # on_click
        list_of_globals = globals()  # list of globals
        list_of_globals['active'] = event.widget.find_closest(
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
            self.calculating_coords(canvas)  # calculate coordinates
        elif event.char == "f":  # if f
            self.update_screen(canvas)  # update screen
        # this will produce an exception but can be ignored
        canvas.move(active, x, y)  # move

    def calculating_coords(self, canvas):  # calculating coordinates
        sensor = canvas.coords(self.sensor)  # sensor
        coord_sensor = [
            sensor[0] + (sensor[2] - sensor[0]), sensor[1] + (sensor[3] - sensor[1])]  # sensor
        sensor_array = []  # sensor array

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

            this_tuple = (tmpVar, corners)  # this tuple
            sensor_array.append(this_tuple)  # sensor array

        return sensor_array  # return sensor array

    def update_screen(self, original_canvas):  # update screen
        objects = self.calculating_coords(original_canvas)  # objects
        self.second_screen.destroy()  # destroy

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
            temp_color = ''  # temp color
            if object[0] == 'Bed':  # if bed
                temp_color = 'red'  # temp color
            elif object[0] == 'Chair':  # if chair
                temp_color = 'yellow'  # temp color
            elif object[0] == 'Sofa':  # if sofa
                temp_color = 'blue'  # temp color

            coordinates = object[1]  # coordinates
            corner0 = coordinates[0]  # corner0
            corner1 = coordinates[2]  # corner1
            self.canvas.create_rectangle(
                corner0[0], corner0[1], corner1[0], corner1[1], fill=temp_color)  # rectangle
# IndexError: invalid index to scalar variable.
        self.update.after(100, self.process_data)  # after 100

    def process_data(self):  # process data
        data = self.q.get()  # data
        self.person_placing(data)  # person placing
        self.create_white_boxes()  # create white boxes
        self.update.after(100, self.process_data)  # after 100

    def person_placing(self, data):  # person placing
        self.canvas.delete('line')  # delete
        self.canvas.delete('whiteBox')  # delete
        coordinate_left_top = data[0]  # coordinate left top
        coordinate_right_top = data[1]  # coordinate right bottom
        # center off mass
        center_x = (
            coordinate_left_top[0] + ((coordinate_right_top[0] - coordinate_left_top[0]) / 2))  # center x
        center_y = (
            coordinate_left_top[1] + ((coordinate_right_top[1] - coordinate_left_top[1]) / 2))  # center y

        self.degrees(center_x)  # degrees
        self.degrees(coordinate_left_top[0])  # degrees
        self.degrees(coordinate_right_top[0])  # degrees

    def degrees(self, center_x):  # degrees
        height_to_middle = 50 + self.var2 * 180 / 2  # height to middle
        point1 = [400 + self.var1 * 180/2, height_to_middle]  # point1

        beta = np.radians(center_x * 3.4375)  # beta

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

    def create_white_boxes(self):  # create white boxes
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
