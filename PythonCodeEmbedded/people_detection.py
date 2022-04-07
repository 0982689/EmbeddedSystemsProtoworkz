from PIL import Image
import cv2 as cv
import numpy as np
import os
import random as rng
from matplotlib import pyplot as plt
rng.seed(12345)

numOfCam = 2

class PeopleDetection:
    def __init__(self):
        # Set threshold values
        self.hMin = 0
        self.sMin = 0
        self.vMin = 0
        self.hMax = 110
        self.sMax = 255
        self.vMax = 255
        self.x = 0
        self.i = 0
        self.max_thresh = 255
        self.thresh = 0
        self.lengthThresh = 4
        self.areaThresh = 10
        self.kernel = 2
        self.imgNumber = -1
        template_folder_staan = './Filtering/Templates/Templates_staan/'
        template_folder_zitten = './Filtering/Templates/Templates_zitten/'
        template_folder_liggen = './Filtering/Templates/Templates_liggen/'
        self.templates_staan = []
        for filename in sorted(os.listdir(template_folder_staan)):
            self.templates_staan.append(
                cv.imread(template_folder_staan + filename))
        self.templates_zitten = []
        for filename in sorted(os.listdir(template_folder_zitten)):
            self.templates_zitten.append(
                cv.imread(template_folder_zitten + filename))
        self.templates_liggen = []
        for filename in sorted(os.listdir(template_folder_liggen)):
            self.templates_liggen.append(
                cv.imread(template_folder_liggen + filename))
        # print(len(self.templates_staan))
        # print(len(self.templates_zitten))
        # print(len(self.templates_liggen))
        print("Init complete")

    def hsvThresh(self, image):
        # imagename = image
        # Load in image
        # image = cv.imread(image)

        output = image
        lower = np.array([0, 0, 0])
        upper = np.array([self.hMax, self.sMax, self.vMax])

        # Create HSV Image and threshold into a range
        hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, lower, upper)
        output = cv.bitwise_and(image, image, mask=mask)

        for i in range(len(output)):
            for j in range(len(output[i])):
                if output[i, j, 0] > 0 or output[i, j, 1] > 0 or output[i, j, 2] > 0:
                    output[i, j] = [255, 255, 255]

        self.bitwiseOperation(output)

    def bitwiseOperation(self, output):
        img1 = output
        # img2 = cv.imread('./Heated_objects.png')
        img2 = output
        img2gray = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
        ret, mask = cv.threshold(img2gray, 10, 255, cv.THRESH_BINARY)
        mask_inv = cv.bitwise_not(mask)
        output = cv.bitwise_and(img1, img1, mask=mask_inv)
        self.thresh_callback(output)

    def thresh_callback(self, image):
        # Add black border (needed for accurate contour detection)
        color = [0, 0, 0]
        top, bottom, left, right = [10]*4
        img_with_border = cv.copyMakeBorder(
            image, top, bottom, left, right, cv.BORDER_CONSTANT, value=color)
        output = img_with_border
        src = img_with_border
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
        areas = []
        for i in range(len(contours)):
            area = cv.contourArea(contours[i])
            length = cv.arcLength(contours[i], True)
            if area >= areaThresh and length >= lengthThresh:
                areas.append(area)
                contoursfixed.append(contours[i])
        # Get the moments
        BiggestContour = []

        BiggestContour.append(contoursfixed[areas.index(max(areas))])

        # print(BiggestContour)
        contours = BiggestContour
        # contours = contoursfixed
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
        People_mask = np.zeros(
            (canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)

        for i in range(len(contours)):
            color = (255, 255, 255)
            cv.drawContours(People_mask, contours, i, color, 1)
            cv.fillPoly(People_mask, pts=contours, color=(255, 255, 255))
        # Cropping image to get rid of previously added black borders

        img2gray = cv.cvtColor(People_mask, cv.COLOR_BGR2GRAY)
        ret, mask = cv.threshold(img2gray, 10, 255, cv.THRESH_BINARY)
        output = cv.bitwise_and(output, output, mask=mask)
        output = output[10:(34*numOfCam), 10:(42*numOfCam)]
        # print(type(output))
        self.templateMatching(output)
        # self.make_templates(output)

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
        cv.imwrite('./Templates/Templates_zitten/' +
                   str(self.x) + '_template.png ', crop)
        print("template saved " + str(self.x))
        self.x = self.x + 1

    def templateMatchingLogic(self, template, img_rgb, templateNumber, state):
        img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
        template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
        w, h = template.shape[::-1]
        res = cv.matchTemplate(img_gray, template, cv.TM_CCOEFF_NORMED)
        threshold = 1
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            cv.rectangle(
                img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), thickness=1)
        for x in range(24):
            for y in range(32):
                if img_rgb[x][y][0] == 0 and img_rgb[x][y][1] == 0 and img_rgb[x][y][2] == 255:
                    # cv.imwrite('./People_images/' + str(self.imgNumber) + '_temp_' +
                    #            str(templateNumber) + '_' + state + '.png', img_rgb)
                    cv.imshow("Image", img_rgb)
                    cv.waitKey(1)
                    # print(pt)
                    # print(pt[0] + w, pt[1] + h)
                    # print("Image saved: " + str(self.imgNumber) +
                    #   ' ' + str(templateNumber))
                    return True

    def templateMatching(self, image):
        # img_rgb = cv.imread('./images/HeatMap_0.png')
        self.imgNumber = self.imgNumber + 1
        templateNumber = 0
        for template in self.templates_staan:
            if(self.templateMatchingLogic(template, image, templateNumber, 'staan')):
                return
            templateNumber += 1
        for template in self.templates_zitten:
            if(self.templateMatchingLogic(template, image, templateNumber, 'zitten')):
                return
            templateNumber += 1
        for template in self.templates_liggen:
            if(self.templateMatchingLogic(template, image, templateNumber, 'liggen')):
                return
            templateNumber += 1
