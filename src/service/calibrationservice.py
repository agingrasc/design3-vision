import cv2
import numpy as np

from camera.camera import Calibration
from camera.camera import CalibrationTargetNotFoundError


class CalibrationService:
    def __init__(self, camera_factory):
        self.camera_factory = camera_factory

    def calibrate_from_images(self, images_path):
        calibration = Calibration(self.camera_factory)
        calibration.add_target_points(self.create_object_points())

        images = self.load_calibration_images(images_path)

        for image in images:
            try:
                calibration.collect_target_image(image)
            except CalibrationTargetNotFoundError:
                print("Calibration target not found on image, skipping image")
                continue

        camera_model = calibration.do_calibration()
        return camera_model.describe()

    def create_object_points(self):
        object_points = np.zeros((6 * 9, 3), np.float32)
        object_points[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)
        return object_points

    def load_calibration_images(self, images_filename):
        return [cv2.imread(filename) for filename in images_filename]
