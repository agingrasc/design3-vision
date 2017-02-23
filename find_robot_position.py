import cv2
import glob

import numpy as np

if __name__ == '__main__':
    images = glob.glob('data/images/robot_targets/*.jpg')

    for filename in images:
        image = cv2.imread(filename)

        image = cv2.medianBlur(image, ksize=5)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_fuchia_hsv = np.array([127, 80, 80])
        higher_fuchia_hsv = np.array([196, 255, 255])

        mask = cv2.inRange(image, lower_fuchia_hsv, higher_fuchia_hsv)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=kernel)

        result = cv2.bitwise_and(image.copy(), image, mask=mask)

        result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
        result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(result, cv2.HOUGH_GRADIENT, 2.0, 20, param1=50, param2=30, minRadius=0, maxRadius=0)

        image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x1, y1, r1) in circles:
                cv2.circle(image, (x1, y1), r1, (0, 255, 0), 2)
                cv2.circle(image, (x1, y1), 1, (255, 0, 0), 2)

            print(filename)
            cv2.imwrite('./data/images/robot_positions/' + filename.split('/')[-1], image)
