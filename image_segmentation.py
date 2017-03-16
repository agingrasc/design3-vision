import glob

import cv2
import numpy as np


def extract_region_of_interest(image, contour):
    x, y, h, w = cv2.boundingRect(contour)
    return image[y:y + w + 20, x:x + h + 20]


def straigthen_figure(image, contour_pts):
    source_points = order_points(contour_pts)

    (tl, tr, br, bl) = source_points
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))

    max_width = max(int(widthA), int(widthB))
    max_height = max_width

    destination_points = np.array([
        [0, 0],
        [max_width, 0],
        [max_width, max_height],
        [0, max_height]], dtype="float32")

    M = cv2.getPerspectiveTransform(source_points, destination_points)
    if M is not None:
        straigthen_image = cv2.warpPerspective(image, M, (max_width, max_height))
        return straigthen_image


def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype="float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect


if __name__ == '__main__':

    for image in glob.glob('./data/images/figures/*.jpg'):
        raw = cv2.imread(image)
        image = raw

        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_green_hsv = np.array([30, 100, 100])
        upper_green_hsv = np.array([80, 255, 255])
        mask = cv2.inRange(image, lower_green_hsv, upper_green_hsv)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=kernel, iterations=2)

        ret, contours, hierachy = cv2.findContours(mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)

        cv2.imshow('Mask', mask)
        cv2.imshow('Image', image)

        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.05 * peri, True)

            if len(approx) == 4 and cv2.contourArea(approx) > 1000 and cv2.isContourConvex(approx):
                src_pts = np.array([x[0] for x in approx])
                inner_figure = straigthen_figure(image, src_pts)
                inner_figure = cv2.medianBlur(inner_figure, ksize=3)

                inner_figure = cv2.cvtColor(inner_figure, cv2.COLOR_BGR2HSV)
                lower_background = np.array([10, 20, 10])
                upper_background = np.array([50, 100, 255])
                figure_mask = cv2.inRange(inner_figure, lower_background, upper_background)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(3, 3))
                figure_mask = cv2.morphologyEx(figure_mask, cv2.MORPH_CLOSE, kernel, iterations=3)
                figure_mask = (255 - figure_mask)

                ret_2, contours_2, hierachy_2 = cv2.findContours(figure_mask.copy(), cv2.RETR_LIST,
                                                                 cv2.CHAIN_APPROX_SIMPLE)

                for contour_2 in contours_2:
                    peri_2 = cv2.arcLength(contour_2, True)
                    approx_2 = cv2.approxPolyDP(contour_2, 0.01 * peri_2, True)

                    if cv2.contourArea(approx_2) > 1000 and len(approx_2) > 4:
                        cv2.drawContours(inner_figure, [approx_2], -1, (10, 255, 255), 2)

                inner_figure = cv2.cvtColor(inner_figure, cv2.COLOR_HSV2BGR)
                cv2.imshow('mask', figure_mask)
                cv2.imshow('square', inner_figure)
                cv2.waitKey()
