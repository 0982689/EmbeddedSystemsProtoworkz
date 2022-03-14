from __future__ import print_function
from __future__ import division
from typing import Counter
from skimage import measure
import cv2 as cv
import numpy as np
import random as rng
rng.seed(12345)


def thresh_callback(val):
    threshold = cv.getTrackbarPos('Canny Thresh:', source_window)
    areaThresh = cv.getTrackbarPos('Length Thresh:', source_window)
    lengthThresh = cv.getTrackbarPos('Size Area:', source_window)
    kernel = cv.getTrackbarPos('kernel size:', source_window)
    canny_output = cv.Canny(src_gray, threshold, threshold * 2)

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
        color = (rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256))
        cv.drawContours(drawing, contours, i, color, 1)
        cv.circle(drawing, (int(mc[i][0]), int(mc[i][1])), 1, color, -1)
    contour_window = 'Contour'
    cv.namedWindow(contour_window)
    cv.imshow(contour_window, drawing)
    if cv.waitKey(33) == ord('k'):
        cv.imwrite('filteredMask.png', drawing)
        print("Image saved")
    if cv.waitKey(33) == ord('q'):
        exit()

    # thresh_callback(length)
    # cv.waitKey()
        # print(contoursfixed)
        # print(type(area))
        # print(type(contours))
        # print(' * Cntour[%d] - Area (M_00) = %.2f - Area OpenCV: %.2f - Length: %.2f' % (i, mu[i]['m00'], cv.contourArea(contours[i]), cv.arcLength(contours[i], True)))


# open image to read
src = cv.imread(cv.samples.findFile(
    '../ThresholdedImages/0_hsvimg.png'))
# convert image to gray and blur it
src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
src_gray = cv.blur(src_gray, (3, 3))
source_window = 'Source'
cv.namedWindow(source_window)
cv.imshow(source_window, src)
max_thresh = 255
thresh = 0  # initial threshold
lengthThresh = 0
areaThresh = 0
kernel = 1
cv.createTrackbar('Canny Thresh:', source_window,
                  thresh, max_thresh, thresh_callback)
cv.createTrackbar('Length Thresh:', source_window,
                  int(lengthThresh), 5000, thresh_callback)
cv.createTrackbar('Size Area:', source_window,
                  int(areaThresh), 5000, thresh_callback)
cv.createTrackbar('kernel size:', source_window, kernel, 10, thresh_callback)
# thresh_callback(thresh, lengthThresh, areaThresh)
cv.waitKey()
