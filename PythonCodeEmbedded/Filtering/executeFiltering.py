import os
import time
# Import classes
import PeopleDetection as PD

PD = PD.PeopleDetection()
# Path to directories
# # Images = './Images/'


# Make time stamp
t0 = time.time()
i = 0
for filename in sorted(os.listdir(Images)):
    print(filename + str(i))
    PD.hsvThresh(Images + filename)
    i += 1

# # Make time stamp
t0 = time.time()

for filename in sorted(os.listdir(Images)):
    PD.hsvThresh(Images + filename)

total = time.time() - t0

print("succesfully segmented images")
print("took: " + str(total))
# PD.templateMatching()
