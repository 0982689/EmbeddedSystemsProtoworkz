import cv2 as cv
import numpy as np 
import random as rng

rng.seed(12345)
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

    def hsvThresh(self, image):
        imagename = image
        # Load in image
        image = cv.imread(image)

        output = image
        lower = np.array([0, 0, 0])
        upper = np.array([self.hMax, self.sMax, self.vMax])

        # Create HSV Image and threshold into a range
        hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, lower, upper)
        output = cv.bitwise_and(image, image, mask=mask)
        
        for i in range(len(output)):
            for j in range(len(output[i])):
                if output[i,j,0] > 0 or output[i,j,1] > 0 or output[i,j,2] > 0:
                    output[i,j] = [255,255,255]
                    
        self.bitwiseOperation(output)


    def bitwiseOperation(self,output):
        img1 = output
        img2 = cv.imread('./Heated_objects.png')
        img2gray = cv.cvtColor(img2,cv.COLOR_BGR2GRAY)
        ret, mask = cv.threshold(img2gray, 10, 255, cv.THRESH_BINARY)
        mask_inv = cv.bitwise_not(mask)
        output = cv.bitwise_and(img1,img1,mask = mask_inv)      
        self.thresh_callback(output)


    def thresh_callback(self,image):
         
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
        #contours = contoursfixed
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
            color = (255,255,255)
            cv.drawContours(People_mask, contours, i, color, 1)
            cv.fillPoly(People_mask,pts=contours,color=(255,255,255))
        # Cropping image to get rid of previously added black borders
        # TODO
        # LET OP DAT DIT UITNEINDELIJK NOG WORD AANGEPAST!!!!!!!!!
        # output = output[10:550, 10:970]
        # output = cv.resize(output, (544, 416), interpolation=cv.INTER_AREA)

        img2gray = cv.cvtColor(People_mask,cv.COLOR_BGR2GRAY)
        ret, mask = cv.threshold(img2gray, 10, 255, cv.THRESH_BINARY)

        # kernel = np.ones((4,4), np.uint8)
        # mask = cv.dilate(mask, kernel, iterations=1)

        output = cv.bitwise_and(output,output,mask = mask)
        cv.imwrite('./People_images/' + str(self.x) +
                   '_hsvimg.png', output)
        self.x = self.x + 1
        #print("image: " +str(self.x))
        #self.people_recognision(image)       

    def people_recognision(self,image):
        output = image

       


