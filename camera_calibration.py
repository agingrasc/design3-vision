import numpy as np
import cv2
import glob
import json

from camera.camera import Calibration

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.
gray_image = None


def create_object_points():
    object_points = np.zeros((6 * 9, 3), np.float32)
    object_points[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)
    return object_points


def load_calibration_images():
    return [cv2.imread(filename) for filename in glob.glob('data/images/calibration/*.jpg')]


def save_camera_model(camera_model):
    with open('./camera_model.json', 'w') as file:
        json.dump(camera_model.describe(), file, indent=4)


if __name__ == "__main__":
    calibration = Calibration()

    calibration.add_target_points(create_object_points())

    images = load_calibration_images()
    for image in images:
        calibration.add_image(image)

    camera_model = calibration.create_camera_model()

    save_camera_model(camera_model)

    # for image_filename in glob.glob('./calibration/*.jpg'):
    #     image = camera.undistort(cv2.imread(image_filename))
    #
    #     print("Saving " + image_filename.split('/')[2])
    #     image_name = image_filename.split('/')[2]
    #     cv2.imwrite('./undistort/' + image_name, image)

    # h, w = image.shape[:2]
    # newcameramtx, roi = cv2.getOptimalNewCameraMatrix(intrinsic_matrix, distortion_matrix, (w, h), 0, (w, h))
