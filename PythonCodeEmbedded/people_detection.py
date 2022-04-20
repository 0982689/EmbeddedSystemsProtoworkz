import cv2 as cv
import numpy as np
import os
import random as rng
import time
from datetime import datetime
rng.seed(12345)
numOfCam = 2  # number of cameras


class People_detection:  # class for people detection
    def __init__(self):  # constructor
        # Set threshold values
        self.hMin = 0  # min hue
        self.sMin = 0  # min saturation
        self.vMin = 0  # min value
        self.hMax = 103  # max hue
        self.sMax = 255  # max saturation
        self.vMax = 255  # max value
        self.x = 0  # template counter
        self.i = 0  # counter for the number of images
        self.max_thresh = 255  # max threshold
        self.thresh = 0  # threshold
        self.lengthThresh = 4  # length of the threshold
        self.areaThresh = 10  # area of the threshold
        self.prev_count = 0  # previous count
        self.kernel = 2  # kernel size
        self.imgNumber = -1  # image number
        self.last_frame = None  # last frame
        self.start_time = 0  # start time
        self.start_timers = False  # start timers
        self.heated_object_picture = cv.imread(
            './NewProject.jpg')  # heated object picture

        # template folder staan
        template_folder_staan = './Filtering/Templates2/Templates_staan/'
        # template folder zitten
        template_folder_zitten = './Filtering/Templates2/Templates_zitten/'
        # template folder liggen
        template_folder_liggen = './Filtering/Templates2/Templates_liggen/'
        self.coords = None  # coordinates of the template
        self.templates_staan = []  # list of templates staan
        # loop through the files in the template folder staan
        for filename in sorted(os.listdir(template_folder_staan)):
            self.templates_staan.append(
                cv.imread(template_folder_staan + filename))  # add the template to the list
        self.templates_zitten = []  # list of templates zitten
        # loop through the files in the template folder zitten
        for filename in sorted(os.listdir(template_folder_zitten)):
            self.templates_zitten.append(
                cv.imread(template_folder_zitten + filename))  # add the template to the list
        self.templates_liggen = []  # list of templates liggen
        # loop through the files in the template folder liggen
        for filename in sorted(os.listdir(template_folder_liggen)):
            self.templates_liggen.append(
                cv.imread(template_folder_liggen + filename))  # add the template to the list
        print(len(self.templates_staan))  # print the number of templates staan
        # print the number of templates zitten
        print(len(self.templates_zitten))
        # print the number of templates liggen
        print(len(self.templates_liggen))

    def hsvThresh(self, image):  # thresholding function

        output = image  # output image
        lower = np.array([0, 0, 0])  # lower threshold
        upper = np.array([self.hMax, self.sMax, self.vMax])  # upper threshold

        # Create HSV Image and threshold into a range
        hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)  # convert to HSV
        mask = cv.inRange(hsv, lower, upper)  # threshold into a range
        output = cv.bitwise_and(image, image, mask=mask)  # bitwise and
        cv.namedWindow("Threshold", cv.WINDOW_NORMAL)  # create window
        cv.resizeWindow("Threshold", 1280, 480)  # resize window
        cv.imshow("Threshold", output)  # show image
        cv.waitKey(1)  # Makes sure window updates
        for i in range(len(output)):  # loop through rows
            for j in range(len(output[i])):  # loop through columns
                # if pixel is not black
                if output[i, j, 0] > 0 or output[i, j, 1] > 0 or output[i, j, 2] > 0:
                    output[i, j] = [255, 255, 255]  # set pixel to white

        # bitwise and with heated object picture
        output = self.bitwiseOperation(output, self.heated_object_picture)
        self.thresh_callback(output)  # call threshold callback function

    def bitwiseOperation(self, input, input2):  # bitwise and function
        # convert to grayscale
        img2gray = cv.cvtColor(input2, cv.COLOR_BGR2GRAY)
        ret, mask = cv.threshold(
            img2gray, 10, 255, cv.THRESH_BINARY)  # threshold
        mask_inv = cv.bitwise_not(mask)  # invert mask
        output = cv.bitwise_and(input, input, mask=mask_inv)  # bitwise and
        return output

    def thresh_callback(self, image):  # threshold callback function

        # Add black border (needed for accurate contour detection)
        color = [0, 0, 0]  # black
        top, bottom, left, right = [10]*4  # border size
        img_with_border = cv.copyMakeBorder(
            image, top, bottom, left, right, cv.BORDER_CONSTANT, value=color)  # add border
        output = img_with_border  # output image
        src = img_with_border  # source image
        # Convert image to gray and blur it
        self.src_gray = cv.cvtColor(
            src, cv.COLOR_BGR2GRAY)  # convert to grayscale
        self.src_gray = cv.blur(self.src_gray, (3, 3))  # blur
        self.source_window = 'Source'  # source window
        self.threshold = self.thresh  # threshold
        areaThresh = self.areaThresh  # area threshold
        lengthThresh = self.lengthThresh  # length threshold
        kernel = self.kernel  # kernel size
        canny_output = cv.Canny(
            self.src_gray, self.threshold, self.threshold * 2)  # Canny edge detection

        kernel = cv.getStructuringElement(
            cv.MORPH_ELLIPSE, (kernel, kernel))  # get structuring element
        dilated = cv.dilate(canny_output, kernel)  # dilate
        # _, contours, _ = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        contours, _ = cv.findContours(
            dilated.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)  # find contours
        contoursfixed = []  # contours fixed
        # Calculate the area with the moments 00 and compare with the result of the OpenCV function
        areas = []  # areas
        for i in range(len(contours)):  # loop through contours
            area = cv.contourArea(contours[i])  # calculate area
            length = cv.arcLength(contours[i], True)  # calculate length
            if area >= areaThresh and length >= lengthThresh:  # if area and length are bigger than threshold
                areas.append(area)  # add area to areas
                # add contour to contoursfixed
                contoursfixed.append(contours[i])
        # Get the moments
        BiggestContour = []  # biggest contour
        # add biggest contour to biggest contour
        BiggestContour.append(contoursfixed[areas.index(max(areas))])

        contours = BiggestContour  # contours
        mu = [None]*len(contours)  # moments
        for i in range(len(contours)):  # loop through contours
            mu[i] = cv.moments(contours[i])  # calculate moments
        # Get the mass centers
        mc = [None]*len(contours)  # mass centers
        for i in range(len(contours)):  # loop through contours
            # add 1e-5 to avoid division by zero
            mc[i] = (mu[i]['m10'] / (mu[i]['m00'] + 1e-5),
                     mu[i]['m01'] / (mu[i]['m00'] + 1e-5))  # calculate mass center

        # Draw contours
        People_mask = np.zeros(
            (canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)  # people mask

        for i in range(len(contours)):  # loop through contours
            color = (255, 255, 255)  # white
            cv.drawContours(People_mask, contours, i,
                            color, 1)  # draw contours
            cv.fillPoly(People_mask, pts=contours, color=(
                255, 255, 255))  # fill polygon
        # Cropping image to get rid of previously added black borders

        # convert to grayscale
        img2gray = cv.cvtColor(People_mask, cv.COLOR_BGR2GRAY)
        ret, mask = cv.threshold(
            img2gray, 10, 255, cv.THRESH_BINARY)  # threshold
        output = cv.bitwise_and(output, output, mask=mask)  # bitwise and
        output = output[10:(34*numOfCam), 10:(42*numOfCam)]  # crop image

        cv.waitKey(1)  # Makes sure window updates
        # Start timer if person remains in same position for long period.
        self.templateMatching(output)  # template matching
        if self.last_frame is not None:  # if last frame is not none
            frame = cv.cvtColor(self.bitwiseOperation(
                output, self.last_frame),  cv.COLOR_BGR2GRAY)  # convert to grayscale
            count = 0  # count
            current_time = time.time()  # current time
            for x in range(frame.shape[0]):  # loop through rows
                for y in range(frame.shape[1]):  # loop through columns
                    if frame[x][y] > 0:  # if pixel is not black
                        count = count + 1  # add to count
            diff = count - self.prev_count  # difference
            threshold = 10  # threshold
            if diff > threshold:  # moving
                self.start_time = time.time()  # start time
                self.last_frame = output  # last frame
                return  # return
            else:  # not moving
                # dont reset timer
                time_not_moving = 5  # time not moving
                # if current time minus start time is greater than time not moving
                if current_time - self.start_time > time_not_moving:
                    print("NOTIFICATION NOT MOVING. ALREADY : " +
                          str(current_time - self.start_time))  # print notification not moving

        self.last_frame = output  # last frame

    def make_templates(self, image):  # make templates
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)  # convert to grayscale
        # threshold
        thresh = cv.threshold(
            gray, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)[1]  # threshold
        hh, ww = thresh.shape  # get shape
        # make bottom 2 rows black where they are white the full width of the image
        thresh[hh-3:hh, 0:ww] = 0
        # get bounds of white pixels
        white = np.where(thresh == 255)
        xmin, ymin, xmax, ymax = np.min(white[1]), np.min(
            white[0]), np.max(white[1]), np.max(white[0])
        # crop the image at the bounds adding back the two blackened rows at the bottom
        crop = image[ymin:ymax+1, xmin:xmax+1]
        # save resulting masked image
        cv.imwrite('./Filtering/Templates2/Templates_liggen/' +
                   str(self.x) + '_template.png ', crop)  # save template
        print("template saved " + str(self.x))  # print template saved
        self.x = self.x + 1  # add to x

    def templateMatchingLogic(self, template, img_rgb):  # template matching logic

        # convert to grayscale
        img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
        # convert to grayscale
        template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
        w, h = template.shape[::-1]  # get shape
        res = cv.matchTemplate(
            img_gray, template, cv.TM_CCOEFF_NORMED)  # match template
        threshold = 0.8  # threshold
        loc = np.where(res >= threshold)  # where res is greater than threshold
        for pt in zip(*loc[::-1]):  # zip
            cv.rectangle(
                img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), thickness=1)  # draw rectangle
        for x in range(24):  # loop through 24
            for y in range(32):  # loop through 32
                if img_rgb[x][y][0] == 0 and img_rgb[x][y][1] == 0 and img_rgb[x][y][2] == 255:  # if red
                    self.coords = [
                        (pt[0], pt[1]), (pt[0] + w, pt[1] + h)]  # coords
                    return True  # return true

    def templateMatching(self, image):  # template matching
        cv.namedWindow("heatmap", cv.WINDOW_NORMAL)  # create window
        cv.resizeWindow("heatmap", 1280, 480)  # resize window
        cv.imshow("heatmap", image)  # show image
        cv.waitKey(1)  # Makes sure window updates
        self.imgNumber = self.imgNumber + 1  # add to img number
        templateNumber = 0
        for template in self.templates_zitten:  # loop through templates
            if(self.templateMatchingLogic(template, image)):  # if template matching logic
                print("Detected: zitten")  # print detected
                return
        for template in self.templates_liggen:  # loop through templates
            if(self.templateMatchingLogic(template, image)):  # if template matching logic
                print("Detected: liggen")  # print detected
                return
        for template in self.templates_staan:  # loop through templates
            if(self.templateMatchingLogic(template, image)):  # if template matching logic
                print("Detected: staan")  # print detected
                return
            templateNumber += 1  # add to template number

    def get_coords(self):  # get coords
        #print("get coords: " + str(self.coords))
        return self.coords
