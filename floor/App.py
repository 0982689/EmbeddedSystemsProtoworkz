from cgi import test
import tkinter as tk
from functools import partial
import numpy as np
import time

global active
active = None

class View:
    def __init__(self, root):
        self.root = root
        self.array = []
        self.initialView()

    def initialView(self):
        root.attributes("-fullscreen", True)

        canvas = tk.Canvas(root, width = 1920, height = 1080)
        canvas.pack()

        canvas.create_text(750,50,fill="black",font="Courier 14", text="Fill in the measurements of your room.")
        
        canvas.create_text(600,100,fill="black",font="Courier 10", text="Length:")
        self.entry1 = tk.Entry (root) 
        canvas.create_window(750, 100, window=self.entry1)

        canvas.create_text(600,125,fill="black",font="Courier 10", text="Width:")
        self.entry2 = tk.Entry (root) 
        canvas.create_window(750, 125, window=self.entry2)

        btn = tk.Button(canvas, text = 'Click for next screen.', command = self.secondView)
        btn.place(x = 688, y = 150)
        canvas.pack()
    
    def secondView(self):
        self.var1 = float(self.entry1.get())
        self.var2 = float(self.entry2.get())

        root.destroy()
        self.secondScreen = tk.Tk()

        self.secondScreen.attributes("-fullscreen", True)

        canvas = tk.Canvas(self.secondScreen, width = 1920, height = 1080)
        canvas.pack()

        self.secondScreen.bind("<Key>", partial(self.keypress, canvas))

        canvas.create_rectangle(400, 50, 400 + self.var1 * 180, 50 + self.var2 * 180, outline = 'blue') 
        self.sensor = canvas.create_rectangle(self.var1 * 180/2 + 395, self.var2 * 180/2 + 45, self.var1 * 180/2 + 405, self.var2 * 180/2 + 55, outline = 'red')
        canvas.pack()    
        
        bedBtn = tk.Button(canvas, text = 'Bed', command = partial(self.bedFunction, canvas))
        bedBtn.place(x = 50, y = 50)
        
        chairBtn = tk.Button(canvas, text = 'Chair', command = partial(self.chairFunction, canvas))
        chairBtn.place(x = 50, y = 100)

        sofaBtn = tk.Button(canvas, text = 'Sofa', command = partial(self.sofaFunction, canvas))
        sofaBtn.place(x = 50, y = 150)

        canvas.pack()       

    def bedFunction(self, canvas):
        bed = canvas.create_rectangle(400, 50, 580, 410,fill= 'red', activefill='cyan')
        listOfGlobals = globals()
        listOfGlobals['active'] = bed
        self.array.append(bed)
        canvas.tag_bind(bed, '<Double-1>', partial(self.onClick, canvas))        

    def chairFunction(self, canvas):
        chair = canvas.create_rectangle(400, 50, 490, 140, fill= 'yellow', activefill='cyan')
        listOfGlobals = globals()
        listOfGlobals['active'] = chair
        self.array.append(chair)
        canvas.tag_bind(chair, '<Double-1>', partial(self.onClick, canvas))

    def sofaFunction(self, canvas):
        sofa = canvas.create_rectangle(400, 50, 580, 320, fill= 'blue', activefill='cyan')
        listOfGlobals = globals()
        listOfGlobals['active'] = sofa
        self.array.append(sofa)
        canvas.tag_bind(sofa, '<Double-1>', partial(self.onClick, canvas))
    
    def onClick(self, canvas, event):
        listOfGlobals = globals()
        listOfGlobals['active'] = event.widget.find_closest(event.x, event.y)

    def keypress(self, canvas, event):
        x, y = 0, 0
        if event.char == "a" : x = -5
        elif event.char == "d" : x = 5
        elif event.char == "w" : y = -5
        elif event.char == "s" : y = 5
        elif event.char == "c" : self.calculatingCoords(canvas)
        elif event.char == "f" : self.updateScreen(canvas)
        canvas.move(active,x,y)
    
    def calculatingCoords(self, canvas):
        sensor = canvas.coords(view.sensor)
        coordSensor = [sensor[0] + (sensor[2] - sensor[0]), sensor[1] + (sensor[3] - sensor[1])]
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
                temp.append(np.degrees(np.arctan((coordSensor[1] - corner[1]) / (coordSensor[0] - corner[0]))))

            thisTuple = (tmpVar, corners)
            sensorArray.append(thisTuple)
        return sensorArray  

    def updateScreen(self, originalCanvas):
        objects = self.calculatingCoords(originalCanvas)
        self.secondScreen.destroy()

        update = tk.Tk()

        update.attributes("-fullscreen", True)

        canvas = tk.Canvas(update, width = 1920, height = 1080)
        canvas.pack()

        canvas.create_rectangle(400, 50, 400 + self.var1 * 180, 50 + self.var2 * 180, outline = 'blue') 
        sensor = canvas.create_rectangle(self.var1 * 180/2 + 395, self.var2 * 180/2 + 45, self.var1 * 180/2 + 405, self.var2 * 180/2 + 55, outline = 'red')
        canvas.pack() 

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
            canvas.create_rectangle(corner0[0], corner0[1], corner1[0], corner1[1], fill = tempColor) 
        
        test = canvas.create_rectangle(400, 50, 400 + self.var1 * 180, 50 + self.var2 * 180, outline = 'blue')



if __name__ == '__main__':
    root = tk.Tk()
    view = View(root)
    root.mainloop()