import os
import time
from multiprocessing.dummy import Pool as ThreadPool

import cv2
import numpy as np

from src.camera.image import Image

times = []

final_images = []


def process_all_images_multithread(images):
    pool = ThreadPool(8)

    pool.map(process_image, images)

    pool.close()
    pool.join()


def process_image(image):
    start = time.time()
    raw_image = image.data

    processed = find_green_square_with_threshold(raw_image)
    contours = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]

    contour_index = 0
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        if len(approx) == 4:
            src_pts = np.array([x[0] for x in approx])

            square = straigthen_figure(raw_image, src_pts)
            square = cv2.medianBlur(square, 3)

            if processed is not None:
                previous_name = image.destination.split('.jpg')
                new_image_id = previous_name[0] + "_" + str(contour_index) + '.jpg'
                contour_index += 1

                new_image_destination = new_image_id
                new_image_filename = new_image_id

                new_image = Image(new_image_id, new_image_filename, new_image_destination, square)

                final_images.append(new_image)

    end = time.time()
    times.append(end - start)


def find_green_square_with_threshold(image):
    processed = cv2.medianBlur(image, 5)
    processed = cv2.cvtColor(processed, cv2.COLOR_BGR2HSV)

    lower_green_hsv = np.array([40, 80, 80])
    upper_green_hsv = np.array([80, 255, 255])

    mask = cv2.inRange(processed, lower_green_hsv, upper_green_hsv)
    kernel = np.ones((15, 15), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def apply_morph(image):
    processed = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed = cv2.Canny(processed, 100, 200)
    return processed


def extract_region_of_interest(image, contour):
    x, y, h, w = cv2.boundingRect(contour)
    return image[y:y + w + 20, x:x + h + 20]


def straigthen_figure(image, contour_pts):
    source_points = order_points(contour_pts)

    max_width = 300
    max_height = 300

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
    current_dir = os.getcwd()
    raw_dir = os.path.join(current_dir, 'raw')
    processed_dir = os.path.join(current_dir, 'processed')

    images = []

    print("Loading raw images...")
    for root, dirs, all_files in os.walk(raw_dir):
        files = [file for file in all_files if file.endswith(".jpg")]

        for image_file in files:
            image_path = os.path.join(raw_dir, image_file)
            image = Image(image_file, image_path, os.path.join(processed_dir, image_file))
            image.load()
            images.append(image)

    start_time = time.time()
    print("Processing {} images...".format(len(images)))

    process_all_images_multithread(images)

    end_time = time.time()
    elapsed = end_time - start_time
    print("\n------------------------------\n")
    print("Total elapsed time: {}s".format(elapsed))
    mean_time = np.mean(times)
    print("Mean time: {}s".format(mean_time))
    median_time = np.median(times)
    print("Median time: {}s".format(median_time))
    image_per_second = len(images) / elapsed
    print("Image per second: {}".format(image_per_second))

    print("\n------------------------------\n")
    print("Saving images...")
    for image in final_images:
        image.save()
