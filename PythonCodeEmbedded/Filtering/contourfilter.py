from __future__ import print_function
from __future__ import division
import cv2 as cv
import numpy as np
import random as rng
rng.seed(12345)


class contourFilter:
    def __init__(self):
        # initial threshold
        # to easily test see contourCalibrate.py and hsvCalibrate.py
        self.i = 0
        self.max_thresh = 255
        self.thresh = 0
        self.lengthThresh = 55
        self.areaThresh = 250
        self.kernel = 2

    def thresh_callback(self, image):
        prefix = image.split("_hsvimg.png")
        imagename = "./FilteredImages/" + prefix[0] + "_Filtered_Image.jpg"
        self.image = image
        src = cv.imread(cv.samples.findFile('./ThresholdedImages/' + image))
        # Convert image to gray and blur it
        self.src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
        self.src_gray = cv.blur(self.src_gray, (3, 3))
        self.source_window = 'Source'
        self.threshold = self.thresh
        areaThresh = self.areaThresh
        lengthThresh = self.lengthThresh
        kernel = self.kernel
        canny_output = cv.Canny(
            self.src_gray, self.threshold, self.threshold * 2)

        kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (kernel, kernel))
        dilated = cv.dilate(canny_output, kernel)
        # _, contours, _ = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        contours, _ = cv.findContours(
            dilated.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contoursfixed = []
        # Calculate the area with the moments 00 and compare with the result of the OpenCV function
        for i in range(len(contours)):
            area = cv.contourArea(contours[i])
            length = cv.arcLength(contours[i], True)
            if area >= areaThresh and length >= lengthThresh:
                contoursfixed.append(contours[i])
        # Get the moments

        contours = contoursfixed
        mu = [None]*len(contours)
        for i in range(len(contours)):
            mu[i] = cv.moments(contours[i])
        # Get the mass centers
        mc = [None]*len(contours)
        for i in range(len(contours)):
            # add 1e-5 to avoid division by zero
            mc[i] = (mu[i]['m10'] / (mu[i]['m00'] + 1e-5),
                     mu[i]['m01'] / (mu[i]['m00'] + 1e-5))

        # Draw contours
        drawing = np.zeros(
            (canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)

        for i in range(len(contours)):
            color = (rng.randint(1, 255), rng.randint(
                1, 255), rng.randint(1, 255))
            cv.drawContours(drawing, contours, i, color, 1)
            cv.circle(drawing, (int(mc[i][0]), int(mc[i][1])), 1, color, -1)
        # Cropping image to get rid of previously added black borders

        # TODO
        # LET OP DAT DIT UITNEINDELIJK NOG WORD AANGEPAST!!!!!!!!!
        # drawing = drawing[10:550, 10:970]

        # drawing = cv.resize(drawing, (544, 416), interpolation=cv.INTER_AREA)
        cv.imwrite(imagename, drawing)
        prefix = imagename.split("./FilteredImages/")
        print("Contour filtering on: " + prefix[1])
        self.i = self.i+1
