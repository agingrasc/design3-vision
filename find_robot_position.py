import cv2
import glob

import numpy as np

if __name__ == '__main__':
    images = glob.glob('data/images/robot_targets/*.jpg')

    for filename in images:
        image = cv2.imread(filename)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_fuchia_hsv = np.array([127, 80, 80])
        higher_fuchia_hsv = np.array([196, 255, 255])

        mask = cv2.inRange(image, lower_fuchia_hsv, higher_fuchia_hsv)
        mask = cv2.bitwise_and(image, mask=mask)

        cv2.imshow('robot targets', mask)

        cv2.waitKey(2000)
