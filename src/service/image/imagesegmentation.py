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
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def find_center_of_mass(contour):
    contour_moments = cv2.moments(contour)
    center_x = int(contour_moments["m10"] / contour_moments["m00"])
    center_y = int(contour_moments["m01"] / contour_moments["m00"])
    return [center_x, center_y]


def segment_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green_hsv = np.array([30, 100, 100])
    upper_green_hsv = np.array([80, 200, 255])
    mask = cv2.inRange(image, lower_green_hsv, upper_green_hsv)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=kernel, iterations=1)
    ret, contours, hierachy = cv2.findContours(mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.045 * peri, True)

        if len(approx) == 4 and cv2.contourArea(approx) > 10000 and cv2.isContourConvex(approx):
            src_pts = np.array([x[0] for x in approx])
            inner_figure = straigthen_figure(image, src_pts)

            inner_figure = cv2.cvtColor(inner_figure, cv2.COLOR_BGR2HSV)
            lower_background = np.array([0, 0, 150])
            upper_background = np.array([180, 50, 255])
            figure_mask = cv2.inRange(inner_figure, lower_background, upper_background)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(3, 3))
            figure_mask = cv2.morphologyEx(figure_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            figure_mask = (255 - figure_mask)

            ret_2, contours_2, hierachy_2 = cv2.findContours(figure_mask.copy(), cv2.RETR_LIST,
                                                             cv2.CHAIN_APPROX_SIMPLE)

            found_segments = []
            for contour_2 in contours_2:
                peri_2 = cv2.arcLength(contour_2, True)
                approx_2 = cv2.approxPolyDP(contour_2, 0.006 * peri_2, True)

                if cv2.contourArea(approx_2) > 15000 and len(approx_2) > 4:
                    found_segments = approx_2
                    cv2.drawContours(inner_figure, [approx_2], -1, (10, 255, 255), 2)

            inner_figure = cv2.cvtColor(inner_figure, cv2.COLOR_HSV2BGR)
            center_of_mass = find_center_of_mass(found_segments)
            cv2.circle(inner_figure, tuple(center_of_mass), 12, (255, 255, 255), 2)
            cv2.circle(inner_figure, tuple(center_of_mass), 2, (255, 255, 255), 1)

            return found_segments, inner_figure, center_of_mass, figure_mask
