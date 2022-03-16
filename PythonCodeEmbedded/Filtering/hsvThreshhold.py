import cv2 as cv
import numpy as np


class hsvThreshHolding:
    def __init__(self):
        # Set threshold values
        self.hMin = 0
        self.sMin = 0
        self.vMin = 0
        self.hMax = 110
        self.sMax = 255
        self.vMax = 255
        self.i = 0

    def hsvThresh(self, image):
        imagename = image
        # Load in image
        image = cv.imread(image)

        output = image
        lower = np.array([self.hMin, self.sMin, self.vMin])
        upper = np.array([self.hMax, self.sMax, self.vMax])

        # Create HSV Image and threshold into a range
        hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, lower, upper)
        output = cv.bitwise_and(image, image, mask=mask)

        # Add black border (needed for accurate contour detection)
        color = [0, 0, 0]
        top, bottom, left, right = [10]*4
        img_with_border = cv.copyMakeBorder(
            output, top, bottom, left, right, cv.BORDER_CONSTANT, value=color)

        cv.imwrite('./ThresholdedImages/' + str(self.i) +
                   '_hsvimg.png', output)
        print("HSV thresholding on:" + imagename)
        self.i = self.i + 1
