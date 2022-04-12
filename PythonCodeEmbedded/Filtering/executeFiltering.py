import os
import time
# Import classes
import PeopleDetection as PD

PD = PD.PeopleDetection()
# Path to directories
Images = '../../heatMaps/zitten/'
#Images = './Images/'

# Make time stamp
t0 = time.time()
for filename in sorted(os.listdir(Images)):
    #filename = os.listdir(Images)[0]
    PD.hsvThresh(Images + filename)

total = time.time() - t0

print("succesfully segmented images")
print("took: " + str(total))
