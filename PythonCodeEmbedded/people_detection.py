from distutils.archive_util import make_archive
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
        self.x = 0  # template counter
        self.prev_count = 0  # previous count
        self.img_number = -1  # image number
        self.last_frame = None  # last frame
        self.start_time = 0  # start time

        self.heated_object_picture = cv.imread(
            './NewProject.jpg')  # heated object picture

        self.coords = None  # coordinates of template

        # template folder standing
        template_folder_standing = './Filtering/Templates_2/Templates_staan/'
        # template folder sitting
        template_folder_sitting = './Filtering/Templates_2/Templates_zitten/'
        # template folder laying
        template_folder_laying = './Filtering/Templates_2/Templates_liggen/'

        self.templates_standing = []  # list of templates standing
        # loop through files in template folder standing
        for filename in sorted(os.listdir(template_folder_standing)):
            self.templates_standing.append(
                cv.imread(template_folder_standing + filename))  # add template to list

        self.templates_sitting = []  # list of templates sitting
        # loop through files in template folder sitting
        for filename in sorted(os.listdir(template_folder_sitting)):
            self.templates_sitting.append(
                cv.imread(template_folder_sitting + filename))  # add template to list
        self.templates_laying = []  # list of templates laying
        # loop through files in template folder laying
        for filename in sorted(os.listdir(template_folder_laying)):
            self.templates_laying.append(
                cv.imread(template_folder_laying + filename))  # add template to list

    def hsv_thresh(self, image):  # thresholding function
        h_max = 103  # max hue
        s_max = 255  # max saturation
        v_max = 255  # max value
        output = image  # output image
        lower = np.array([0, 0, 0])  # lower threshold
        upper = np.array([h_max, s_max, v_max])  # upper threshold

        # Create HSV Image and threshold into a range
        hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)  # convert to HSV
        mask = cv.inRange(hsv, lower, upper)  # threshold into a range
        output = cv.bitwise_and(image, image, mask=mask)  # bitwise and

        # uncomment for debugging
        # cv.namedWindow("Threshold", cv.WINDOW_NORMAL)  # create window
        # cv.resizeWindow("Threshold", 1280, 480)  # resize window
        # cv.imshow("Threshold", output)  # show image
        # cv.waitKey(1)  # Makes sure window updates
        for i in range(len(output)):  # loop through rows
            for j in range(len(output[i])):  # loop through columns
                # if pixel is not black
                if output[i, j, 0] > 0 or output[i, j, 1] > 0 or output[i, j, 2] > 0:
                    output[i, j] = [255, 255, 255]  # set pixel to white

        # bitwise and with heated object picture
        output = self.bitwise_operation(output, self.heated_object_picture)
        self.thresh_callback(output)  # call threshold callback function

    def bitwise_operation(self, input, input_2):  # bitwise and function
        # convert to grayscale
        img_2_gray = cv.cvtColor(input_2, cv.COLOR_BGR2GRAY)
        ret, mask = cv.threshold(
            img_2_gray, 10, 255, cv.THRESH_BINARY)  # threshold
        mask_inv = cv.bitwise_not(mask)  # invert mask
        output = cv.bitwise_and(input, input, mask=mask_inv)  # bitwise and
        return output

    def thresh_callback(self, image):  # threshold callback function

        threshold = 0  # threshold
        area_thresh = 10  # area threshold
        length_thresh = 4   # length threshold
        kernel = 2  # kernel size

        # Add black border (needed for accurate contour detection)
        color = [0, 0, 0]  # black
        top, bottom, left, right = [10]*4  # border size
        img_with_border = cv.copyMakeBorder(
            image, top, bottom, left, right, cv.BORDER_CONSTANT, value=color)  # add border
        output = img_with_border  # output image
        # Convert image to gray and blur it
        src_gray = cv.cvtColor(
            img_with_border, cv.COLOR_BGR2GRAY)  # convert to grayscale
        src_gray = cv.blur(src_gray, (3, 3))  # blur
        canny_output = cv.Canny(
            src_gray, threshold, threshold * 2)  # Canny edge detection

        kernel = cv.getStructuringElement(
            cv.MORPH_ELLIPSE, (kernel, kernel))  # get structuring element
        dilated = cv.dilate(canny_output, kernel)  # dilate
        # _, contours, _ = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        contours, _ = cv.findContours(
            dilated.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)  # find contours
        contours_fixed = []  # contours fixed
        # Calculate area with moments 00 and compare with result of OpenCV function
        areas = []  # areas
        for i in range(len(contours)):  # loop through contours
            area = cv.contourArea(contours[i])  # calculate area
            length = cv.arcLength(contours[i], True)  # calculate length
            if area >= area_thresh and length >= length_thresh:  # if area and length are bigger than threshold
                areas.append(area)  # add area to areas
                # add contour to contours_fixed
                contours_fixed.append(contours[i])
        # Get moments
        biggest_contour = []  # biggest contour
        # add biggest contour to biggest contour
        biggest_contour.append(contours_fixed[areas.index(max(areas))])

        contours = biggest_contour  # contours
        mu = [None]*len(contours)  # moments
        for i in range(len(contours)):  # loop through contours
            mu[i] = cv.moments(contours[i])  # calculate moments
        # Get mass centers
        mc = [None]*len(contours)  # mass centers
        for i in range(len(contours)):  # loop through contours
            # add 1e-5 to avoid division by zero
            mc[i] = (mu[i]['m10'] / (mu[i]['m00'] + 1e-5),
                     mu[i]['m01'] / (mu[i]['m00'] + 1e-5))  # calculate mass center

        # Draw contours
        people_mask = np.zeros(
            (canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)  # people mask

        for i in range(len(contours)):  # loop through contours
            color = (255, 255, 255)  # white
            cv.drawContours(people_mask, contours, i,
                            color, 1)  # draw contours
            cv.fillPoly(people_mask, pts=contours, color=(
                255, 255, 255))  # fill polygon
        # Cropping image to get rid of previously added black borders

        # convert to grayscale
        img_2_gray = cv.cvtColor(people_mask, cv.COLOR_BGR2GRAY)
        ret, mask = cv.threshold(
            img_2_gray, 10, 255, cv.THRESH_BINARY)  # threshold
        output = cv.bitwise_and(output, output, mask=mask)  # bitwise and
        output = output[10:(34*numOfCam), 10:(42*numOfCam)]  # crop image

        cv.waitKey(1)  # Makes sure window updates
        # Start timer if person remains in same position for long period.
        self.template_matching(output)  # template matching
        if self.last_frame is not None:  # if last frame is not none
            frame = cv.cvtColor(self.bitwise_operation(
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
        # uncomment to make templates
        # self.make_templates(output)  # make templates

    def make_templates(self, image):  # make templates
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)  # convert to grayscale
        # threshold
        thresh = cv.threshold(
            gray, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)[1]  # threshold
        hh, ww = thresh.shape  # get shape
        # make bottom 2 rows black where they are white full width of image
        thresh[hh-3:hh, 0:ww] = 0
        # get bounds of white pixels
        white = np.where(thresh == 255)
        xmin, ymin, xmax, ymax = np.min(white[1]), np.min(
            white[0]), np.max(white[1]), np.max(white[0])
        # crop image at bounds adding back two blackened rows at bottom
        crop = image[ymin:ymax+1, xmin:xmax+1]
        # save resulting masked image
        cv.imwrite('./Filtering/Templates2/Templates_liggen/' +
                   str(self.x) + '_template.png ', crop)  # save template
        print("template saved " + str(self.x))  # print template saved
        self.x = self.x + 1  # add to x

    def template_matching_logic(self, template, img_rgb):  # template matching logic

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

    def template_matching(self, image):  # template matching
        # uncomment for debugging
        # cv.namedWindow("heatmap", cv.WINDOW_NORMAL)  # create window
        # cv.resizeWindow("heatmap", 1280, 480)  # resize window
        # cv.imshow("heatmap", image)  # show image
        # cv.waitKey(1)  # Makes sure window updates
        self.img_number = self.img_number + 1  # add to img number
        for template in self.templates_sitting:  # loop through templates
            if(self.template_matching_logic(template, image)):  # if template matching logic
                print("Detected: zitten")  # print detected
                return
        for template in self.templates_laying:  # loop through templates
            if(self.template_matching_logic(template, image)):  # if template matching logic
                print("Detected: liggen")  # print detected
                return
        for template in self.templates_standing:  # loop through templates
            if(self.template_matching_logic(template, image)):  # if template matching logic
                print("Detected: staan")  # print detected
                return

    def get_coords(self):  # get coords
        return self.coords
