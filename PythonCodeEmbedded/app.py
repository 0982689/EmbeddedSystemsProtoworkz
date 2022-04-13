import tkinter as tk
from functools import partial
import numpy as np

global active
active = None


def create_canvas(screen, width, height):
    return tk.Canvas(screen, width=width, height=height)


def on_click(event):
    list_of_globals = globals()
    list_of_globals['active'] = event.widget.find_closest(event.x, event.y)


class View:
    def __init__(self, root, q):
        self.q = q
        self.root = root
        self.array = []
        self.initial_view()
        self.update = None
        self.sensor = None
        self.entry1 = None
        self.entry2 = None
        self.second_screen = None
        self.update_canvas = None

    def initial_view(self):
        self.root.attributes("-fullscreen", True)

        canvas = tk.Canvas(self.root, width=1920, height=1080).pack()

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
                        command=self.second_view)
        btn.place(x=688, y=150).pack()

    def second_view(self):
        self.entry1 = float(self.entry1.get())
        self.entry2 = float(self.entry2.get())

        self.root.destroy()

        self.second_screen = tk.Tk()

        self.second_screen.attributes("-fullscreen", True)

        canvas = create_canvas(
            self.second_screen, width=1920, height=1080).pack()

        self.second_screen.bind("<Key>", partial(self.keypress, canvas))

        canvas.create_rectangle(
            400, 50, 400 + self.entry1 * 180, 50 + self.entry2 * 180, outline='blue')
        self.sensor = canvas.create_rectangle(
            self.entry1 * 180 / 2 + 395, self.entry2 *
            180 / 2 + 45, self.entry1 * 180 / 2 + 405,
            self.entry2 * 180 / 2 + 55, outline='red')
        canvas.pack()

        tk.Button(canvas, text='Bed',
                  command=partial(self.furniture_function, canvas, 'red', 'cyan', 400, 50, 580, 410)).place(x=50, y=50)

        tk.Button(canvas, text='Chair',
                  command=partial(self.furniture_function, canvas, 'yellow', 'cyan', 400, 50, 490, 140)).place(x=50,
                                                                                                               y=100)

        tk.Button(canvas, text='Sofa',
                  command=partial(self.furniture_function, canvas, 'blue', 'cyan', 400, 50, 580, 320)).place(x=50,
                                                                                                             y=150)

        canvas.pack()

    def furniture_function(self, canvas, fill, active_fill, top_left, top_right, bottom_left, bottom_right):
        list_of_globals = globals()
        list_of_globals['active'] = canvas.create_rectangle(top_left, top_right, bottom_left, bottom_right, fill=fill,
                                                            activefill=active_fill)
        self.array.append(list_of_globals['active'])
        canvas.tag_bind(list_of_globals['active'],
                        '<Double-1>', partial(on_click, canvas))

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
            self.calculating_coords(canvas)
        elif event.char == "f":
            self.update_screen(canvas)
        canvas.move(active, x, y)

    def calculating_coords(self, canvas):
        sensor = canvas.coords(self.sensor)
        coord_sensor = [
            sensor[0] + (sensor[2] - sensor[0]), sensor[1] + (sensor[3] - sensor[1])]
        sensor_array = []
        corners = []

        for item in self.array:
            coords = canvas.coords(item)
            corners.clear()

            tmp_str = ""
            x = coords[2] - coords[0]
            y = coords[3] - coords[1]

            if x == 180 and y == 360:
                tmp_str = "Bed"
            elif x == 90 and y == 90:
                tmp_str = "Chair"
            elif x == 180 and y == 270:
                tmp_str = "Sofa"

            corners.append([coords[0], coords[1]])
            corners.append([coords[2], coords[1]])
            corners.append([coords[2], coords[3]])
            corners.append([coords[0], coords[3]])

            temp = []
            temp.clear()
            for corner in corners:
                temp.append(np.degrees(
                    np.arctan((coord_sensor[1] - corner[1]) / (coord_sensor[0] - corner[0]))))
            sensor_array.append((tmp_str, corners))
        return sensor_array

    def update_screen(self, original_canvas):
        objects = self.calculating_coords(original_canvas)
        self.second_screen.destroy()

        self.update = tk.Tk()

        self.update.attributes("-fullscreen", True)

        self.update_canvas = create_canvas(
            self.update, width=1920, height=1080)
        self.update_canvas.pack()

        self.update_canvas.create_rectangle(
            400, 50, 400 + self.entry1 * 180, 50 + self.entry2 * 180, outline='black')
        self.update_canvas.create_rectangle(self.entry1 * 180 / 2 + 395, self.entry2 * 180 /
                                            2 + 45, self.entry1 * 180 / 2 + 405, self.entry2 * 180 / 2 + 55,
                                            outline='red')
        self.update_canvas.pack()

        for object in objects:
            temp_color = ''
            if object[0] == 'Bed':
                temp_color = 'red'
            elif object[0] == 'Chair':
                temp_color = 'yellow'
            elif object[0] == 'Sofa':
                temp_color = 'blue'

            coordinates = object[1]
            corner0 = coordinates[0]
            corner1 = coordinates[2]
            self.update_canvas.create_rectangle(
                corner0[0], corner0[1], corner1[0], corner1[1], fill=temp_color)
        # IndexError: invalid index to scalar variable.
        self.update.after(100, self.process_data)

    def process_data(self):
        data = self.q.get()
        self.person_placing(data)
        self.create_white_boxes()
        self.update.after(100, self.process_data)

    def person_placing(self, data):
        print("Person Placing")
        self.update_canvas.delete('line')
        self.update_canvas.delete('whiteBox')
        coordinate_left_top = data[0]
        print("left top: " + str(coordinate_left_top))
        coordinate_right_bottom = data[1]
        # center off mass
        center_x = (
            coordinate_left_top[0] + ((coordinate_right_bottom[0] - coordinate_left_top[0]) / 2))
        center_y = (
            coordinate_left_top[1] + ((coordinate_right_bottom[1] - coordinate_left_top[1]) / 2))

        self.degrees(center_x)
        self.degrees(coordinate_left_top[0])
        self.degrees(coordinate_right_bottom[0])

    def degrees(self, center_x):
        height_to_middle = 50 + self.entry2 * 180 / 2
        point1 = [400 + self.entry1 * 180 / 2, height_to_middle]

        beta = np.radians(center_x * 3.4375)

        tmp = 0
        if np.degrees(beta) == 90:
            point2 = [400 + self.entry1 * 180 / 2, 50 + self.entry2 * 180]
            self.update_canvas.create_line(
                point1[0], point1[1], point2[0], point2[1], tag='line')
            return
        elif np.degrees(beta) == 270:
            point2 = [400 + self.entry1 * 180 / 2, 50]
            self.update_canvas.create_line(
                point1[0], point1[1], point2[0], point2[1], tag='line')
            return
        elif np.degrees(beta) < 90:
            tmp = 270
            left = False
        elif np.degrees(beta) < 180:
            left = True
            tmp = 90
        elif np.degrees(beta) < 270:
            tmp = 90
            left = True
        elif np.degrees(beta) < 360:
            tmp = 270
            left = False
        else:
            left = None

        alpha = np.radians(360 - tmp - np.degrees(beta))

        width = self.entry1 * 180
        a = width / 2
        b = (a * np.sin(beta)) / np.sin(alpha)
        # Drawing line c
        if left:
            point2 = [400, 540 / 2 + b + 50]
        else:
            point2 = [400 + width, 540 / 2 + b + 50]

        self.update_canvas.create_line(point1[0], point1[1],
                                       point2[0], point2[1], tag='line')

    def create_white_boxes(self):
        self.update_canvas.create_rectangle(
            0, 0, 400, 1080, fill='white', outline="", tags="whiteBox")
        self.update_canvas.create_rectangle(
            0, 0, 1920, 50, fill='white', outline="", tags="whiteBox")
        self.update_canvas.create_rectangle(401 + self.entry2 * 180,
                                            0, 1920, 1080, fill='white', outline="", tags="whiteBox")
        self.update_canvas.create_rectangle(0, 51 + self.entry2 * 180,
                                            1920, 1080, fill='white', outline="", tags="whiteBox")


def start(q):
    root = tk.Tk()
    view = View(root, q)
    root.mainloop()
