import os
import time
# Import classes
import hsvThreshhold as hsv
import contourfilter as ctr

hsv = hsv.hsvThreshHolding()
ctr = ctr.contourFilter()

# Path to directories
hsvdir = './Images/'
ctrdir = './ThresholdedImages/'

# Make time stamp
t0 = time.time()

for filename in sorted(os.listdir(hsvdir)):
    hsv.hsvThresh(hsvdir + filename)

for filename in sorted(os.listdir(ctrdir)):
    ctr.thresh_callback(filename)

total = time.time() - t0

print("succesfully segmented images")
print("took: " + str(total))
