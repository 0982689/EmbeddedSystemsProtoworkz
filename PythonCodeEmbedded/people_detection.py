import cv2 as cv
import numpy as np
import os
import random as rng
import time
from threading import Thread
rng.seed(12345)
NUMOFCAM = 2


class Image_editing:
    def __init__(self):
        # Set threshold values
        self.template_number = 0
        self.prev_count = 0
        self.img_number = -1
        self.last_frame = None
        self.start_time = 0
        self.start_timers = False
        self.heated_object_picture = cv.imread('./Heated_objects_black.png')
        template_folders = ['./Filtering/Templates/Templates_staan/',
                            './Filtering/Templates/Templates_zitten/', './Filtering/Templates/Templates_liggen/']
        self.coords = None
        self.template_list = []
        for template_folder in template_folders:
            self.read_templates(template_folder)

    def read_templates(self, folder):
        temp_template_list = []
        for filename in sorted(os.listdir(folder)):
            temp_template_list.append(
                cv.imread(folder + filename))
        self.template_list.append(temp_template_list)

    def hsv_thresh(self, image):
        h_max = 110
        s_max = 255
        v_max = 255
        lower = np.array([0, 0, 0])
        upper = np.array([h_max, s_max, v_max])
        # Create HSV Image and threshold into a range
        hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, lower, upper)
        output = cv.bitwise_and(image, image, mask=mask)

        for i in range(len(output)):
            for j in range(len(output[i])):
                if output[i, j, 0] > 0 or output[i, j, 1] > 0 or output[i, j, 2] > 0:
                    output[i, j] = [255, 255, 255]

        output = self.bitwise_operation(output, self.heated_object_picture)
        self.thresh_callback(output)

    def bitwise_operation(self, input, input2):
        img_gray = cv.cvtColor(input2, cv.COLOR_BGR2GRAY)
        _, mask = cv.threshold(img_gray, 10, 255, cv.THRESH_BINARY)
        mask_inv = cv.bitwise_not(mask)
        output = cv.bitwise_and(input, input, mask=mask_inv)
        return output

    def thresh_callback(self, image):
        threshold = 0
        areaThresh = 10
        lengthThresh = 4
        kernel = 2
        # Add black border (needed for accurate contour detection)
        color = [0, 0, 0]
        top, bottom, left, right = [10]*4
        img_with_border = cv.copyMakeBorder(
            image, top, bottom, left, right, cv.BORDER_CONSTANT, value=color)
        
        output = img_with_border
        # Convert image to gray and blur it
        src_gray = cv.cvtColor(img_with_border, cv.COLOR_BGR2GRAY)
        src_gray = cv.blur(src_gray, (3, 3))
        canny_output = cv.Canny(
            src_gray, threshold, threshold * 2)
        kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (kernel, kernel))
        dilated = cv.dilate(canny_output, kernel)
        # _, contours, _ = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        contours, _ = cv.findContours(
            dilated.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contoursfixed = []
        # Calculate the area with the moments 00 and compare with the result of the OpenCV function
        areas = []
        for i in range(len(contours)):
            area = cv.contourArea(contours[i])
            length = cv.arcLength(contours[i], True)
            if area >= areaThresh and length >= lengthThresh:
                areas.append(area)
                contoursfixed.append(contours[i])
        # Get the moments
        contours = []
        contours.append(contoursfixed[areas.index(max(areas))])
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
        people_mask = np.zeros(
            (canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
        for i in range(len(contours)):
            color = (255, 255, 255)
            cv.drawContours(people_mask, contours, i, color, 1)
            cv.fillPoly(people_mask, pts=contours, color=(255, 255, 255))
        img2gray = cv.cvtColor(people_mask, cv.COLOR_BGR2GRAY)
        _, mask = cv.threshold(img2gray, 10, 255, cv.THRESH_BINARY)
        output = cv.bitwise_and(output, output, mask=mask)
        output = output[10:(34*NUMOFCAM), 10:(42*NUMOFCAM)]
        # self.templateMatching(output)
        # if self.last_frame is not None:
        #     frame = cv.cvtColor(self.bitwise_operation(
        #         output, self.last_frame),  cv.COLOR_BGR2GRAY)
        #     count = 0
        #     current_time = time.time()
        #     count_threshhold = 100
        #     thresh_hold = 100
        #     for x in range(frame.shape[0]):
        #         for y in range(frame.shape[1]):
        #             if frame[x][y] > 0:
        #                 count = count + 1
        #     if count - self.prev_count > count_threshhold:
        #         self.last_frame = output
        #         return
        #     if count > thresh_hold:
        #         self.start_timers = True
        #         self.start_time = time.time()
        #     elif self.start_timers is True and count < thresh_hold and current_time - self.start_time > 60:
        #         print(str(current_time - self.start_time))
        #     self.prev_count = count
        # self.last_frame = output
        self.make_templates(output)           # enable this to make templates

    def make_templates(self, image):
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        # threshold
        thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)[1]
        hh, ww = thresh.shape
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
                   str(self.template_number) + '_template.png ', crop)
        print("template saved " + str(self.template_number))
        self.template_number = self.template_number + 1

    def template_matching_logic(self, template, img_rgb):
        pt = None
        img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
        template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
        w, h = template.shape[::-1]
        res = cv.matchTemplate(img_gray, template, cv.TM_CCOEFF_NORMED)
        threshold = 0.6
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            cv.rectangle(
                img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), thickness=1)
        for x in range(24):
            for y in range(32):
                if img_rgb[x][y][0] == 0 and img_rgb[x][y][1] == 0 and img_rgb[x][y][2] == 255:
                    try:
                        self.coords = [(pt[0], pt[1]), (pt[0] + w, pt[1] + h)]
                    except:
                        pass
                    return True

    def thread_templates(self, image, templateID):
        # this can be deleted in final version. In this version it is used to detect which template is being used
        templateNumber = 0
        for template in self.template_list[templateID]:
            if(self.template_matching_logic(template, image)):
                print("Detected: " + str(templateID))
                return
            templateNumber += 1

    def templateMatching(self, image):
        self.img_number = self.img_number + 1
        t1 = Thread(target=self.thread_templates,   # standing
                    args=(image, 0))
        t2 = Thread(target=self.thread_templates,    # sitting
                    args=(image, 1))
        t3 = Thread(target=self.thread_templates,   # laying down
                    args=(image, 2))
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()

    def get_coords(self):
        return self.coords
