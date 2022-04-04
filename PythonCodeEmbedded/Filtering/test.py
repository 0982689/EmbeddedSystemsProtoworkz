import cv2 as cv
import numpy as np

# load image as grayscale
img = cv.imread('./Templates_black/0_template.png')

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# threshold 
thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)[1]
hh, ww = thresh.shape

# make bottom 2 rows black where they are white the full width of the image
thresh[hh-3:hh, 0:ww] = 0

# get bounds of white pixels
white = np.where(thresh==255)
xmin, ymin, xmax, ymax = np.min(white[1]), np.min(white[0]), np.max(white[1]), np.max(white[0])
print(xmin,xmax,ymin,ymax)

# crop the image at the bounds adding back the two blackened rows at the bottom
crop = img[ymin:ymax+1, xmin:xmax+1]

# save resulting masked image
cv.imwrite('xray_chest_thresh.jpg', thresh)
cv.imwrite('xray_chest_crop.jpg', crop)

# display result
cv.imshow("thresh", thresh)
cv.imshow("crop", crop)
cv.waitKey(0)
cv.destroyAllWindows()

# gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
# print(gray)
# dimensions = gray.shape
# height = gray.shape[0]
# width = gray.shape[1]
# print('Image Dimension    : ',dimensions)
# print('Image Height       : ',height)
# print('Image Width        : ',width)
# cv.imshow('gray', img)
# cv.waitKey(0)