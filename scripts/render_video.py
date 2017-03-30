import re
import cv2
import glob

import datetime


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)', text)]


if __name__ == '__main__':
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    _out = cv2.VideoWriter()
    _out.open('/Users/jeansebastien/Desktop/robot_feed-{}.avi'.format(datetime.datetime.now()), fourcc, 5, (1120, 840), True)

    images = glob.glob('./data/images/robot_feed/*.jpg')
    images.sort(key=natural_keys)

    images_data = []

    print("Loading {} images...".format(len(images)))
    for filename in images:
        images_data.append(cv2.imread(filename))

    print("Rendering video...")
    for image in images_data:
        _out.write(image)

    _out.release()
