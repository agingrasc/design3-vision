import cv2
import numpy as np

from config import LOWER_BACKGROUND, UPPER_BACKGROUND, LOWER_FIGURE_HSV, UPPER_FIGURE_HSV


class NoSegmentsFound(Exception):
    pass


def extract_region_of_interest(image, contour):
    x, y, h, w = cv2.boundingRect(contour)
    return image[y:y + w + 20, x:x + h + 20]


def straigthen_figure(image, contour_pts):
    source_points = order_points(contour_pts)

    (tl, tr, br, bl) = source_points

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))

    max_width = max(int(widthA), int(widthB))
    max_height = max_width

    destination_points = np.array([
        [0, 0],
        [max_width, 0],
        [max_width, max_height],
        [0, max_height]], dtype="float32")

    M = cv2.getPerspectiveTransform(source_points, destination_points)

    if M is not None:
        return cv2.warpPerspective(image, M, (max_width, max_height))


def order_points(pts):
    rectangle = np.zeros((4, 2), dtype="float32")

    total_sum = pts.sum(axis=1)
    rectangle[0] = pts[np.argmin(total_sum)]
    rectangle[2] = pts[np.argmax(total_sum)]

    diff = np.diff(pts, axis=1)
    rectangle[1] = pts[np.argmin(diff)]
    rectangle[3] = pts[np.argmax(diff)]

    return rectangle


def find_center_of_mass(contour):
    contour_moments = cv2.moments(contour)
    center_x = int(contour_moments["m10"] / contour_moments["m00"])
    center_y = int(contour_moments["m01"] / contour_moments["m00"])
    return [center_x, center_y]


def threshold_green(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(image, LOWER_FIGURE_HSV, UPPER_FIGURE_HSV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=kernel, iterations=1)
    image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
    return mask


def segment_image(image):
    mask = threshold_green(image)

    ret, contours, hierachy = cv2.findContours(mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    figure_found = False

    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.045 * perimeter, True)

        if len(approx) == 4 and cv2.contourArea(approx) > 9000 and cv2.isContourConvex(approx) and not figure_found:
            src_pts = np.array([x[0] for x in approx])
            inner_figure = straigthen_figure(image, src_pts)

            inner_figure = cv2.cvtColor(inner_figure, cv2.COLOR_BGR2HSV)
            figure_mask = cv2.inRange(inner_figure, LOWER_BACKGROUND, UPPER_BACKGROUND)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(3, 3))
            figure_mask = cv2.morphologyEx(figure_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            figure_mask = (255 - figure_mask)

            ret_2, contours_2, hierachy_2 = cv2.findContours(
                figure_mask.copy(),
                cv2.RETR_LIST,
                cv2.CHAIN_APPROX_SIMPLE
            )

            found_segments = []
            for contour_2 in contours_2:
                peri_2 = cv2.arcLength(contour_2, True)
                approx_2 = cv2.approxPolyDP(contour_2, 0.006 * peri_2, True)

                if cv2.contourArea(approx_2) > 15000 and len(approx_2) > 4:
                    found_segments = approx_2
                    cv2.drawContours(inner_figure, [approx_2], -1, (10, 255, 255), 2)

            inner_figure = cv2.cvtColor(inner_figure, cv2.COLOR_HSV2BGR)

            if len(found_segments) > 0:
                center_of_mass = find_center_of_mass(found_segments)

                cv2.circle(inner_figure, tuple(center_of_mass), 12, (255, 255, 255), 2)
                cv2.circle(inner_figure, tuple(center_of_mass), 2, (255, 255, 255), 1)

                figure_found = True

    if figure_found:
        return found_segments, inner_figure, center_of_mass, figure_mask
    else:
        raise NoSegmentsFound
